import uuid
from datetime import timedelta

from sqlalchemy import select

from src.domain.rules import utcnow
from src.infrastructure import models as m

CLIENTE = {"nome": "Loja Exemplo Ltda", "documento": "11222333000181", "tipo": "PJ", "email": "contato@exemplo.com"}


def _criar_cliente(client, headers):
    r = client.post("/customers", json=CLIENTE, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _pedido(client, headers, cid):
    q = client.post("/quotes", json={"customer_id": cid, "origem": "São Paulo/SP", "destino": "Recife/PE",
                                     "peso_kg": 100, "volume_m3": 1}, headers=headers)
    assert q.status_code == 201, q.text
    o = client.post("/orders", json={"quote_id": q.json()["id"]}, headers=headers)
    assert o.status_code == 201, o.text
    return q.json()["id"], o.json()["id"]


def _eventos(session_factory):
    with session_factory() as s:
        return [e.routing_key for e in s.scalars(select(m.OutboxEvent))]


def test_sem_token_retorna_401(client):
    assert client.post("/customers", json=CLIENTE).status_code == 401


def test_fluxo_completo_e_eventos(client, cliente, atendente, session_factory):
    cid = _criar_cliente(client, cliente)
    _, oid = _pedido(client, cliente, cid)
    assert client.get(f"/orders/{oid}", headers=cliente).json()["status"] == "CRIADO"

    t = client.post("/tickets", json={"customer_id": cid, "order_id": oid, "categoria": "ATRASO",
                                      "prioridade": "ALTA", "assunto": "Atraso", "mensagem": "Onde está?"}, headers=cliente)
    assert t.status_code == 201
    tid = t.json()["id"]
    assert client.post(f"/tickets/{tid}/messages", json={"mensagem": "Verificando"}, headers=atendente).status_code == 201
    detalhe = client.get(f"/tickets/{tid}", headers=cliente).json()
    assert detalhe["status"] == "EM_ATENDIMENTO" and len(detalhe["messages"]) == 2

    sin = client.post("/claims", json={"order_id": oid, "tipo": "AVARIA", "descricao": "Caixa danificada",
                                       "valor_reclamado": "150.00"}, headers=cliente)
    assert sin.status_code == 201
    assert client.get(f"/claims/{sin.json()['id']}", headers=cliente).status_code == 200

    # RN04: não pode avaliar antes de entregue
    fb = {"target": "ENTREGA", "nota": 5, "order_id": oid}
    assert client.post("/feedback", json=fb, headers=cliente).status_code == 422
    assert client.patch(f"/orders/{oid}/status", json={"status": "ENTREGUE"}, headers=atendente).status_code == 200
    assert client.post("/feedback", json=fb, headers=cliente).status_code == 201
    assert client.post("/feedback", json=fb, headers=cliente).status_code == 409  # uma avaliação por pedido

    ev = _eventos(session_factory)
    for esperado in ["customer.cotacao.solicitada", "customer.pedido.criado", "customer.chamado.aberto",
                     "customer.sinistro.registrado", "customer.entrega.avaliada", "customer.cliente.notificado"]:
        assert esperado in ev


def test_documento_duplicado_e_invalido(client, cliente, outro_cliente):
    _criar_cliente(client, cliente)
    assert client.post("/customers", json=CLIENTE, headers=outro_cliente).status_code == 409
    ruim = {**CLIENTE, "documento": "11222333000199"}
    assert client.post("/customers", json=ruim, headers=cliente).status_code == 422


def test_rn02_cliente_nao_acessa_dados_de_outro(client, cliente, outro_cliente, atendente):
    cid = _criar_cliente(client, cliente)
    _, oid = _pedido(client, cliente, cid)
    assert client.get(f"/orders/{oid}", headers=outro_cliente).status_code == 403
    assert client.get(f"/customers/{cid}", headers=outro_cliente).status_code == 403
    assert client.get(f"/orders/{oid}", headers=atendente).status_code == 200  # equipe vê tudo


def test_cliente_nao_altera_status_do_pedido(client, cliente):
    cid = _criar_cliente(client, cliente)
    _, oid = _pedido(client, cliente, cid)
    assert client.patch(f"/orders/{oid}/status", json={"status": "ENTREGUE"}, headers=cliente).status_code == 403


def test_rn01_cotacao_expirada_e_reuso(client, cliente, session_factory):
    cid = _criar_cliente(client, cliente)
    qid, _ = _pedido(client, cliente, cid)
    assert client.post("/orders", json={"quote_id": qid}, headers=cliente).status_code == 409  # já usada

    q2 = client.post("/quotes", json={"customer_id": cid, "origem": "Origem", "destino": "Destino", "peso_kg": 1, "volume_m3": 1},
                     headers=cliente).json()["id"]
    with session_factory() as s:
        quote = s.get(m.Quote, uuid.UUID(q2))
        quote.expires_at = utcnow() - timedelta(minutes=1)
        s.commit()
    assert client.post("/orders", json={"quote_id": q2}, headers=cliente).status_code == 422


def test_rn06_pedido_cancelado_nao_aceita_sinistro(client, cliente, atendente):
    cid = _criar_cliente(client, cliente)
    _, oid = _pedido(client, cliente, cid)
    client.patch(f"/orders/{oid}/status", json={"status": "CANCELADO"}, headers=atendente)
    r = client.post("/claims", json={"order_id": oid, "tipo": "AVARIA", "descricao": "xx", "valor_reclamado": "1"},
                    headers=cliente)
    assert r.status_code == 422


def test_ticket_resolvido_nao_recebe_mensagem(client, cliente, atendente):
    cid = _criar_cliente(client, cliente)
    t = client.post("/tickets", json={"customer_id": cid, "categoria": "DUVIDA", "assunto": "Dúvida", "mensagem": "Oi"},
                    headers=cliente).json()["id"]
    client.patch(f"/tickets/{t}/status", json={"status": "RESOLVIDO"}, headers=atendente)
    assert client.post(f"/tickets/{t}/messages", json={"mensagem": "mais"}, headers=cliente).status_code == 422


def test_rastreamento_indisponivel_retorna_503(client, cliente):
    cid = _criar_cliente(client, cliente)
    _, oid = _pedido(client, cliente, cid)
    assert client.get(f"/orders/{oid}/tracking", headers=cliente).status_code == 503
