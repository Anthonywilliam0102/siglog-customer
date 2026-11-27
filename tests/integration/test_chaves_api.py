"""Chaves de API emitidas pelo CRM para outros squads consultarem pedidos (somente leitura)."""
from sqlalchemy import select

from src.infrastructure import models as m
from tests.integration.test_fluxo_api import _criar_cliente, _pedido


def _emitir(client, atendente, squad="wms"):
    r = client.post("/settings/api-keys", json={"squad": squad, "nome": "Integração de teste"}, headers=atendente)
    assert r.status_code == 201, r.text
    return r.json()


def test_so_a_equipe_emite_lista_e_revoga(client, cliente, atendente):
    assert client.post("/settings/api-keys", json={"squad": "wms", "nome": "abc"}, headers=cliente).status_code == 403
    assert client.get("/settings/api-keys", headers=cliente).status_code == 403
    k = _emitir(client, atendente)
    assert client.delete(f"/settings/api-keys/{k['id']}", headers=cliente).status_code == 403


def test_chave_aparece_uma_vez_e_so_o_hash_fica_no_banco(client, atendente, session_factory):
    k = _emitir(client, atendente)
    assert k["chave"].startswith("sk_") and k["prefixo"] == k["chave"][:8]
    assert k["chave"] not in client.get("/settings/api-keys", headers=atendente).text
    with session_factory() as s:
        reg = s.scalar(select(m.ApiKey))
        assert reg.key_hash != k["chave"] and k["chave"] not in reg.key_hash


def test_chave_le_pedidos_mas_nao_escreve(client, cliente, atendente):
    oid = _pedido(client, cliente, _criar_cliente(client, cliente))[1]
    h = {"X-API-Key": _emitir(client, atendente)["chave"]}
    assert client.get(f"/orders/{oid}", headers=h).status_code == 200
    assert len(client.get("/orders", headers=h).json()) == 1
    assert client.patch(f"/orders/{oid}/status", json={"status": "EM_SEPARACAO"}, headers=h).status_code == 401
    assert client.get("/settings/integrations", headers=h).status_code == 401
    assert client.get("/settings/api-keys", headers=h).status_code == 401


def test_chave_invalida_ou_revogada_e_negada(client, atendente):
    assert client.get("/orders", headers={"X-API-Key": "sk_errada"}).status_code == 401
    k = _emitir(client, atendente)
    assert client.get("/orders", headers={"X-API-Key": k["chave"]}).status_code == 200
    assert client.delete(f"/settings/api-keys/{k['id']}", headers=atendente).json()["revoked_at"]
    assert client.get("/orders", headers={"X-API-Key": k["chave"]}).status_code == 401
    assert client.get("/settings/api-keys", headers=atendente).json()[0]["last_used_at"]
