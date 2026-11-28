"""Cabeçalhos de segurança nas respostas da API (middleware ASGI puro).

HSTS só é enviado quando a requisição chegou por HTTPS (direto ou via proxy com X-Forwarded-Proto),
para não afetar o uso local em HTTP.
"""

FIXOS = [(b"x-content-type-options", b"nosniff"), (b"x-frame-options", b"DENY"), (b"referrer-policy", b"no-referrer")]
HSTS = (b"strict-transport-security", b"max-age=31536000; includeSubDomains")


class CabecalhosDeSeguranca:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        https = scope.get("scheme") == "https" or headers.get(b"x-forwarded-proto", b"").split(b",")[0].strip() == b"https"

        async def enviar(msg):
            if msg["type"] == "http.response.start":
                existentes = {k.lower() for k, _ in msg.get("headers", [])}
                extra = [h for h in FIXOS if h[0] not in existentes]
                if https and HSTS[0] not in existentes:
                    extra.append(HSTS)
                msg = {**msg, "headers": [*msg.get("headers", []), *extra]}
            await send(msg)

        return await self.app(scope, receive, enviar)
