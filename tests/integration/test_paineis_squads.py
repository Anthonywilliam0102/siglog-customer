"""Painéis de WMS/Financeiro no pedido, status das integrações e teste de conexão."""
import httpx
import pytest
from cryptography.fernet import Fernet

from src.config.settings import settings
from src.infrastructure.clients import url_segura
from tests.integration.test_fluxo_api import _criar_cliente, _pedido


@pytest.fixture()
def cfg(monkeypatch):
    monkeypatch.setattr(settings, "settings_encryption_key", Fernet.generate_key().decode())
    monkeypatch.setattr("src.application.services.validar_base_url",
                        lambda u: url_segura.validar_base_url(u, resolve=lambda h, p: ["93.184.216.34"]))


def _resp(status=200, corpo=None):
    return httpx.Response(status, json=corpo or {}, request=httpx.Request("GET", "https://x"))


def test_paineis_simulados_seguem_o_status(client, cliente, atendente, monkeypatch):
    monkeypatch.setattr(settings, "tracking_mock", True)
    oid = _pedido(client, cliente, _criar_cliente(client, cliente))[1]
    p = {x["squad"]: x for x in client.get(f"/orders/{oid}/squads", headers=cliente).json()}
    assert set(p) == {"wms", "financeiro"} and all(x["fonte"] == "simulado" for x in p.values())
    assert p["wms"]["status"] == "Aguardando separação" and p["financeiro"]["status"] == "Cobrança pendente"
    for st in ("EM_SEPARACAO", "EM_TRANSPORTE", "ENTREGUE"):
        client.patch(f"/orders/{oid}/status", json={"status": st}, headers=atendente)
    p = {x["squad"]: x for x in client.get(f"/orders/{oid}/squads", headers=cliente).json()}
    assert p["wms"]["status"] == "Enviado ao transporte" and p["financeiro"]["status"] == "Paga"


def test_rn02_painel_de_outro_cliente_e_negado(client, cliente, outro_cliente):
    oid = _pedido(client, cliente, _criar_cliente(client, cliente))[1]
    assert client.get(f"/orders/{oid}/squads", headers=outro_cliente).status_code in (403, 404)


def test_sem_mock_e_sem_url_diz_nao_configurada(client, cliente, monkeypatch):
    monkeypatch.setattr(settings, "tracking_mock", False)
    oid = _pedido(client, cliente, _criar_cliente(client, cliente))[1]
    assert {x["fonte"] for x in client.get(f"/orders/{oid}/squads", headers=cliente).json()} == {"nao_configurada"}


def test_painel_real_usa_a_chave_e_traduz(client, cliente, atendente, cfg, monkeypatch):
    oid = _pedido(client, cliente, _criar_cliente(client, cliente))[1]
    client.put("/settings/integrations/wms", headers=atendente,
               json={"base_url": "https://wms.exemplo.com", "header_name": "X-Key", "api_key": "segredo-123"})
    visto = {}

    def falso(url, **kw):
        visto.update(url=url, headers=kw["headers"])
        return _resp(corpo={"status": "EM_SEPARACAO", "itens_separados": 2, "itens_total": 4})

    monkeypatch.setattr(httpx, "get", falso)
    p = next(x for x in client.get(f"/orders/{oid}/squads", headers=cliente).json() if x["squad"] == "wms")
    assert p["fonte"] == "integracao" and p["status"] == "Em separação"
    assert p["detalhes"][0]["valor"] == "2 de 4"
    assert visto["url"] == f"https://wms.exemplo.com/separacao/pedidos/{oid}" and visto["headers"] == {"X-Key": "segredo-123"}
    assert "segredo-123" not in client.get(f"/orders/{oid}/squads", headers=cliente).text


def test_painel_indisponivel_nao_derruba_a_tela(client, cliente, atendente, cfg, monkeypatch):
    oid = _pedido(client, cliente, _criar_cliente(client, cliente))[1]
    client.put("/settings/integrations/financeiro", headers=atendente, json={"base_url": "https://fin.exemplo.com"})

    def falha(url, **kw):
        raise httpx.ConnectError("x")

    monkeypatch.setattr(httpx, "get", falha)
    r = client.get(f"/orders/{oid}/squads", headers=cliente)
    assert r.status_code == 200
    assert next(x for x in r.json() if x["squad"] == "financeiro")["fonte"] == "indisponivel"


def test_status_das_integracoes_nao_expoe_url_nem_chave(client, cliente, atendente, cfg, monkeypatch):
    monkeypatch.setattr(settings, "tracking_mock", False)
    client.put("/settings/integrations/wms", headers=atendente,
               json={"base_url": "https://wms.exemplo.com", "api_key": "segredo-123"})
    r = client.get("/integrations/status", headers=cliente)
    assert r.status_code == 200 and "wms.exemplo" not in r.text and "segredo-123" not in r.text
    modos = {x["squad"]: x["modo"] for x in r.json()}
    assert modos == {"wms": "configurada", "frota": "nao_prevista", "tracking": "nao_configurada",
                     "financeiro": "nao_configurada", "rh": "nao_prevista"}


def test_testar_conexao(client, cliente, atendente, cfg, monkeypatch):
    assert client.post("/settings/integrations/wms/test", headers=cliente).status_code == 403
    client.put("/settings/integrations/wms", headers=atendente, json={"base_url": "https://wms.exemplo.com"})
    monkeypatch.setattr(httpx, "get", lambda url, **kw: _resp(200))
    r = client.post("/settings/integrations/wms/test", headers=atendente).json()
    assert r["ok"] is True and r["status_http"] == 200

    def falha(url, **kw):
        raise httpx.ConnectError("x")

    monkeypatch.setattr(httpx, "get", falha)
    r = client.post("/settings/integrations/wms/test", headers=atendente).json()
    assert r["ok"] is False and r["erro"]
