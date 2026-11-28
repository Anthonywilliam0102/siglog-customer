"""Teste de segurança SEGURO contra a produção (só leitura + tentativas que DEVEM ser recusadas).

Uso (na máquina do executor, depois de o deploy da correção estar Live):
  API_URL=https://siglog-customer-api.onrender.com WEB_URL=https://siglog-customer.pages.dev \
  SUPABASE_URL=... SUPABASE_PUBLISHABLE_KEY=... CLIENTE_EMAIL=... CLIENTE_PW=... ATENDENTE_EMAIL=... ATENDENTE_PW=... \
  python scripts/seguranca_producao.py

Regras de segurança do próprio teste:
- nunca imprime senhas, tokens ou chaves; nunca cria chamados, pedidos, clientes nem chaves de API;
- nenhuma requisição de carga (poucas dezenas de chamadas no total);
- o único teste que poderia gravar algo (URL interna na integração) é seguido de limpeza e conferência.
Sem credenciais, roda só as verificações anônimas.
"""
import json
import os
import sys
import time
import uuid

import httpx

API = os.environ.get("API_URL", "https://siglog-customer-api.onrender.com").rstrip("/")
WEB = os.environ.get("WEB_URL", "https://siglog-customer.pages.dev").rstrip("/")
resultados: list[tuple[str, str, str]] = []


def ok(nome: str, cond: bool, detalhe: str = "") -> None:
    resultados.append(("OK   " if cond else "FALHA", nome, "" if cond else detalhe))


def pular(nome: str, motivo: str) -> None:
    resultados.append(("PULOU", nome, motivo))


def req(metodo, caminho, token=None, **kw):
    h = kw.pop("headers", {})
    if token:
        h["Authorization"] = f"Bearer {token}"
    return httpx.request(metodo, API + caminho, headers=h, timeout=90, **kw)


def entrar(email_var, pw_var):
    env = {k: os.environ.get(k) for k in ("SUPABASE_URL", "SUPABASE_PUBLISHABLE_KEY", email_var, pw_var)}
    if not all(env.values()):
        return None
    r = httpx.post(f"{env['SUPABASE_URL'].rstrip('/')}/auth/v1/token?grant_type=password", timeout=30,
                   headers={"apikey": env["SUPABASE_PUBLISHABLE_KEY"]}, json={"email": env[email_var], "password": env[pw_var]})
    return r.json().get("access_token") if r.status_code == 200 else None


def jwt_falso(segredo, role="gestor", alg="HS256"):
    import base64
    import hashlib
    import hmac

    def b64(b):
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

    cab = b64(json.dumps({"alg": alg, "typ": "JWT"}).encode())
    corpo = b64(json.dumps({"sub": "atacante", "role": role, "exp": int(time.time()) + 3600}).encode())
    if alg == "none":
        return f"{cab}.{corpo}."
    ass = b64(hmac.new(segredo.encode(), f"{cab}.{corpo}".encode(), hashlib.sha256).digest())
    return f"{cab}.{corpo}.{ass}"


def anonimo():
    # acorda a API (plano free hiberna)
    r = req("GET", "/health")
    ok("API no ar (/health 200)", r.status_code == 200, str(r.status_code))
    hh = {k.lower(): v for k, v in r.headers.items()}
    ok("API: Strict-Transport-Security presente", "max-age" in hh.get("strict-transport-security", ""), hh.get("strict-transport-security", "ausente"))
    ok("API: X-Content-Type-Options nosniff", hh.get("x-content-type-options") == "nosniff", hh.get("x-content-type-options", "ausente"))
    for rota in ("/orders", "/customers", "/tickets", "/claims", "/me", "/settings/integrations", "/settings/api-keys"):
        ok(f"sem token: GET {rota} -> 401", req("GET", rota).status_code == 401)
    ok("sem token: /metrics recusado (401/403)", req("GET", "/metrics").status_code in (401, 403),
       "o /metrics está público (a correção ainda não está no ar?)")
    for seg in ("secret", "changeme", "siglog_dev", "jwt-secret", "dev-secret-change-me-please-32chars!!"):
        r = req("GET", "/me", token=jwt_falso(seg))
        ok(f"JWT HS256 forjado com segredo '{seg[:6]}…' recusado", r.status_code == 401, str(r.status_code))
    ok("JWT alg=none recusado", req("GET", "/me", token=jwt_falso("", alg="none")).status_code == 401)
    ok("chave de API inventada recusada", req("GET", "/orders", headers={"X-API-Key": "sk_" + "a" * 43}).status_code == 401)
    r = req("GET", f"/orders/{uuid.uuid4()}", token="lixo")
    ok("erro sem vazamento de detalhes internos", not any(x in r.text.lower() for x in ("traceback", "sqlalchemy", "psycopg", "/app/", "postgresql://")),
       r.text[:120])
    r = req("GET", "/health", headers={"Origin": "https://site-malicioso.example"})
    ok("CORS não reflete origem não autorizada", r.headers.get("access-control-allow-origin") in (None, ""),
       r.headers.get("access-control-allow-origin", ""))
    r = req("POST", "/customers", content=b'{"nome":"' + b"A" * 300_000 + b'"}', headers={"Content-Type": "application/json"})
    ok("corpo de 300 KB recusado antes da autenticação (413) ou 401", r.status_code in (413, 401), str(r.status_code))


def front():
    try:
        r = httpx.get(WEB + "/", timeout=60, follow_redirects=True)
    except httpx.HTTPError as exc:
        return ok("front no ar", False, type(exc).__name__)
    h = {k.lower(): v for k, v in r.headers.items()}
    ok("front no ar", r.status_code == 200, str(r.status_code))
    ok("front: X-Content-Type-Options nosniff", h.get("x-content-type-options") == "nosniff", h.get("x-content-type-options", "ausente"))
    ok("front: X-Frame-Options DENY", h.get("x-frame-options", "").upper() == "DENY", h.get("x-frame-options", "ausente"))
    ok("front: Content-Security-Policy presente", "default-src" in h.get("content-security-policy", ""), "ausente")
    ok("front: Strict-Transport-Security presente", "max-age" in h.get("strict-transport-security", ""), h.get("strict-transport-security", "ausente"))


def autenticado(tok_cli, tok_at):
    if not tok_cli:
        pular("testes com conta de cliente", "sem credenciais ou login falhou")
    else:
        for m, rota in (("GET", "/settings/integrations"), ("GET", "/settings/api-keys"), ("POST", "/settings/integrations/wms/test")):
            ok(f"cliente: {m} {rota} -> 403", req(m, rota, tok_cli).status_code == 403)
        r = req("POST", "/settings/api-keys", tok_cli, json={"squad": "wms", "nome": "tentativa do cliente"})
        ok("cliente não consegue emitir chave de API (403)", r.status_code == 403, str(r.status_code))
        r = req("PATCH", f"/orders/{uuid.uuid4()}/status", tok_cli, json={"status": "ENTREGUE"})
        ok("cliente não altera status de pedido (403/404)", r.status_code in (403, 404), str(r.status_code))
        r = req("GET", "/integrations/status", tok_cli)
        ok("status das integrações sem URL nem chave", r.status_code == 200 and "http" not in r.text and "api_key" not in r.text, r.text[:100])
        r = req("GET", f"/orders/{uuid.uuid4()}", tok_cli)
        ok("pedido inexistente/alheio: 403/404, nunca 500", r.status_code in (403, 404), str(r.status_code))
        # validação de entrada: tudo deve ser recusado ANTES de gravar (customer_id inexistente também barra a gravação)
        cid = str(uuid.uuid4())
        base = {"customer_id": cid, "origem": "São Paulo/SP", "destino": "Recife/PE", "peso_kg": 10, "volume_m3": 1}
        for nome, corpo in (("peso negativo", {**base, "peso_kg": -1}), ("origem gigante", {**base, "origem": "A" * 5000}),
                            ("peso texto", {**base, "peso_kg": "abc"}), ("uuid inválido", {**base, "customer_id": "x"})):
            r = req("POST", "/quotes", tok_cli, json=corpo)
            ok(f"cotação inválida ({nome}) -> 422", r.status_code == 422, str(r.status_code))
        raw = ('{"customer_id":"%s","origem":"AA","destino":"BB","peso_kg":Infinity,"volume_m3":1}' % cid).encode()
        r = req("POST", "/quotes", tok_cli, content=raw, headers={"Content-Type": "application/json"})
        ok("JSON com Infinity -> 422 (nunca 500)", r.status_code == 422, str(r.status_code))
        r = req("POST", "/tickets", tok_cli, json={"customer_id": cid, "categoria": "ATRASO", "prioridade": "MEDIA", "assunto": "teste",
                                                   "mensagem": "x" * 6000})
        ok("mensagem de 6000 caracteres -> 422", r.status_code == 422, str(r.status_code))
        r = req("POST", "/customers", tok_cli, content=b'{"nome":"' + b"A" * 300_000 + b'"}', headers={"Content-Type": "application/json"})
        ok("corpo de 300 KB -> 413", r.status_code == 413, str(r.status_code))
    if not tok_at:
        pular("testes com conta de equipe (SSRF)", "sem credenciais ou login falhou")
        return
    antes = {i["squad"]: i["base_url"] for i in req("GET", "/settings/integrations", tok_at).json()}
    try:
        for alvo in ("http://169.254.169.254/latest/meta-data", "https://127.0.0.1", "https://10.0.0.5", "https://localhost",
                     "https://exemplo.com:22", "file:///etc/passwd", "https://user:pw@exemplo.com"):
            r = req("PUT", "/settings/integrations/frota", tok_at, json={"base_url": alvo})
            ok(f"SSRF recusado: {alvo[:40]}", r.status_code in (400, 422), f"{r.status_code} {r.text[:80]}")
        r = req("PUT", "/settings/integrations/frota", tok_at, json={"header_name": "X-Key\r\nX-Evil: 1"})
        ok("injeção no nome do cabeçalho recusada", r.status_code == 422, str(r.status_code))
    finally:  # limpeza: devolve o campo da Frota ao valor de antes caso algum teste tenha sido aceito por engano
        depois = {i["squad"]: i["base_url"] for i in req("GET", "/settings/integrations", tok_at).json()}
        if depois.get("frota") != antes.get("frota"):
            req("PUT", "/settings/integrations/frota", tok_at, json={"base_url": antes.get("frota") or ""})
            ok("limpeza: URL da Frota não foi alterada pelos testes", False, "FOI ALTERADA e foi restaurada: investigar")
        else:
            ok("URL da Frota intacta depois dos testes de SSRF", True)


if __name__ == "__main__":
    print(f"API: {API}\nFront: {WEB}\n(nenhum segredo é impresso)\n")
    anonimo()
    front()
    autenticado(entrar("CLIENTE_EMAIL", "CLIENTE_PW"), entrar("ATENDENTE_EMAIL", "ATENDENTE_PW"))
    for estado, nome, det in resultados:
        print(estado, nome, f"({det})" if det else "")
    falhas = [r for r in resultados if r[0] == "FALHA"]
    print(f"\n{sum(r[0].startswith('OK') for r in resultados)} OK · {len(falhas)} FALHA · {sum(r[0] == 'PULOU' for r in resultados)} puladas")
    sys.exit(1 if falhas else 0)
