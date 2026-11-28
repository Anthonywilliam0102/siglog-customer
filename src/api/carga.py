"""Proteção contra sobrecarga: limita as requisições em andamento e recusa o excesso NA ENTRADA com 503.

Sem isso, o excesso fica numa fila de threads (as rotas são síncronas) e tudo, até o /health, deixa de responder.
Middleware ASGI puro (sem BaseHTTPMiddleware) para não adicionar custo por requisição.
"""
import json

ISENTOS = ("/health", "/metrics")


class LimiteDeRequisicoes:
    def __init__(self, app, maximo: int):
        self.app = app
        self.maximo = maximo
        self.em_andamento = 0

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or self.maximo <= 0 or scope["path"] in ISENTOS:
            return await self.app(scope, receive, send)
        if self.em_andamento >= self.maximo:
            corpo = json.dumps({"detail": "Servidor ocupado, tente novamente em instantes"}).encode()
            await send({"type": "http.response.start", "status": 503, "headers": [
                (b"content-type", b"application/json"), (b"content-length", str(len(corpo)).encode()), (b"retry-after", b"2")]})
            return await send({"type": "http.response.body", "body": corpo})
        self.em_andamento += 1
        try:
            return await self.app(scope, receive, send)
        finally:
            self.em_andamento -= 1


class LimiteDeCorpo:
    """Recusa com 413 requisições cujo Content-Length passa do máximo (evita corpos gigantes). 0 desliga."""

    def __init__(self, app, maximo: int):
        self.app = app
        self.maximo = maximo

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and self.maximo > 0:
            for nome, valor in scope.get("headers", []):
                if nome == b"content-length" and valor.isdigit() and int(valor) > self.maximo:
                    corpo = json.dumps({"detail": "Corpo da requisição grande demais"}).encode()
                    await send({"type": "http.response.start", "status": 413, "headers": [
                        (b"content-type", b"application/json"), (b"content-length", str(len(corpo)).encode())]})
                    return await send({"type": "http.response.body", "body": corpo})
        return await self.app(scope, receive, send)
