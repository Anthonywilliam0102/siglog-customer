"""Popula a API com dados FICTÍCIOS de demonstração (pedidos em vários status, chamados, sinistros e avaliações).

Uso (a API precisa estar no ar; cria registros de verdade no banco que ela usa):
  # Modo dev (API com JWT_SECRET):      API_URL=http://localhost:8000 JWT_SECRET=... python scripts/seed_demo.py --sim
  # Modo Supabase (login real):         API_URL=... SUPABASE_URL=... SUPABASE_ANON_KEY=... \\
  #   CLIENTE_EMAIL=... CLIENTE_PW=... ATENDENTE_EMAIL=... ATENDENTE_PW=... python scripts/seed_demo.py --sim
Rodar duas vezes duplica os dados. Nunca imprime senhas ou tokens.
"""
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request

API = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")


def http(method, url, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {}


def token(quem):
    if os.environ.get("SUPABASE_URL"):
        st, d = http("POST", os.environ["SUPABASE_URL"].rstrip("/") + "/auth/v1/token?grant_type=password",
                     {"email": os.environ[f"{quem.upper()}_EMAIL"], "password": os.environ[f"{quem.upper()}_PW"]},
                     {"apikey": os.environ["SUPABASE_ANON_KEY"]})
        if st != 200:
            sys.exit(f"Login do {quem} falhou (HTTP {st}).")
        return d["access_token"]
    import jwt  # modo dev
    papel = "cliente" if quem == "cliente" else "atendente"
    claims = {"sub": f"demo-{papel}", "role": papel, "exp": int(time.time()) + 3600}
    return jwt.encode(claims, os.environ["JWT_SECRET"], algorithm="HS256")


def cnpj():
    d = [random.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]
    for n, p in ((12, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]), (13, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])):
        r = sum(x * y for x, y in zip(d[:n], p, strict=True)) % 11
        d.append(0 if r < 2 else 11 - r)
    return "".join(map(str, d))


def main():
    if "--sim" not in sys.argv:
        sys.exit("Isto cria dados de demonstração no banco da API. Rode novamente com --sim para confirmar.")
    hc = {"Authorization": f"Bearer {token('cliente')}"}
    ha = {"Authorization": f"Bearer {token('atendente')}"}
    ok = lambda r, msg: (r[0] < 300) or sys.exit(f"{msg}: HTTP {r[0]} {r[1]}")  # noqa: E731

    st, clientes = http("GET", f"{API}/customers?limit=5", headers=hc)
    if not clientes:
        r = http("POST", f"{API}/customers", {"nome": "Loja Horizonte Ltda", "tipo": "PJ", "documento": cnpj(), "email": "contato@horizonte.example"}, hc)
        ok(r, "cadastro do cliente")
        cid = r[1]["id"]
    else:
        cid = clientes[0]["id"]
    print("cliente:", cid[:8])

    rotas = [("São Paulo/SP", "Recife/PE", 120.5, 1.2), ("Curitiba/PR", "Porto Alegre/RS", 40, 0.4), ("Belo Horizonte/MG", "Salvador/BA", 310, 2.8),
             ("Rio de Janeiro/RJ", "Brasília/DF", 75, 0.9), ("Manaus/AM", "Belém/PA", 220, 2.1)]
    alvo = ["CRIADO", "EM_SEPARACAO", "EM_TRANSPORTE", "ENTREGUE", "ENTREGUE"]
    passos = ["EM_SEPARACAO", "EM_TRANSPORTE", "ENTREGUE"]
    pedidos = []
    for (o, d, kg, m3), final in zip(rotas, alvo, strict=True):
        q = http("POST", f"{API}/quotes", {"customer_id": cid, "origem": o, "destino": d, "peso_kg": kg, "volume_m3": m3}, hc)
        ok(q, "cotação")
        p = http("POST", f"{API}/orders", {"quote_id": q[1]["id"]}, hc)
        ok(p, "pedido")
        for s in passos[: passos.index(final) + 1] if final != "CRIADO" else []:
            ok(http("PATCH", f"{API}/orders/{p[1]['id']}/status", {"status": s}, ha), "status")
        pedidos.append((p[1]["id"], final))
    print("pedidos:", len(pedidos))

    entregues = [i for i, f in pedidos if f == "ENTREGUE"]
    http("POST", f"{API}/feedback", {"target": "ENTREGA", "nota": 5, "order_id": entregues[0], "comentario": "Chegou antes do prazo."}, hc)
    http("POST", f"{API}/feedback", {"target": "ENTREGA", "nota": 4, "order_id": entregues[1]}, hc)

    tickets = [("Atraso na coleta", "ATRASO", "ALTA", "A coleta prevista para hoje não aconteceu. Podem verificar?", pedidos[1][0]),
               ("Dúvida sobre cobrança", "COBRANCA", "MEDIA", "Qual a data de vencimento da cobrança deste pedido?", pedidos[2][0]),
               ("Alteração de endereço", "OUTRO", "BAIXA", "Preciso alterar o endereço de entrega.", pedidos[0][0])]
    ids = []
    for assunto, cat, pri, msg, oid in tickets:
        t = http("POST", f"{API}/tickets", {"customer_id": cid, "order_id": oid, "categoria": cat, "prioridade": pri, "assunto": assunto, "mensagem": msg}, hc)
        ok(t, "chamado")
        ids.append(t[1]["id"])
    ok(http("POST", f"{API}/tickets/{ids[1]}/messages", {"mensagem": "Olá! Estamos verificando com o financeiro e retornamos ainda hoje."}, ha), "resposta")
    http("POST", f"{API}/tickets/{ids[2]}/messages", {"mensagem": "Endereço atualizado conforme solicitado."}, ha)
    http("PATCH", f"{API}/tickets/{ids[2]}/status", {"status": "RESOLVIDO"}, ha)
    http("POST", f"{API}/feedback", {"target": "ATENDIMENTO", "nota": 5, "ticket_id": ids[2], "comentario": "Rápido e educado."}, hc)
    print("chamados:", len(ids))

    http("POST", f"{API}/claims", {"order_id": entregues[1], "tipo": "AVARIA", "descricao": "Duas caixas chegaram amassadas.", "valor_reclamado": "180.00"}, hc)
    http("POST", f"{API}/claims", {"order_id": pedidos[2][0], "tipo": "ATRASO", "descricao": "Carga parada no centro de distribuição.", "valor_reclamado": "0"}, hc)
    print("sinistros: 2\nOK: dados de demonstração criados.")


if __name__ == "__main__":
    main()
