from src.config.settings import settings
from tests.integration.test_fluxo_api import _criar_cliente, _pedido


def test_rastreamento_mock_segue_o_status_do_pedido(client, cliente, atendente, monkeypatch):
    monkeypatch.setattr(settings, "tracking_mock", True)
    cid = _criar_cliente(client, cliente)
    _, oid = _pedido(client, cliente, cid)

    t = client.get(f"/orders/{oid}/tracking", headers=cliente).json()
    assert t["source"] == "mock" and t["events"] == [] and t["status"] == "Aguardando separação"

    for st in ("EM_SEPARACAO", "EM_TRANSPORTE"):
        client.patch(f"/orders/{oid}/status", json={"status": st}, headers=atendente)
    t = client.get(f"/orders/{oid}/tracking", headers=cliente).json()
    assert t["status"] == "Em trânsito" and len(t["events"]) == 2

    client.patch(f"/orders/{oid}/status", json={"status": "ENTREGUE"}, headers=atendente)
    t = client.get(f"/orders/{oid}/tracking", headers=cliente).json()
    assert t["status"] == "Entregue" and len(t["events"]) == 4


def test_mock_desligado_mantem_503(client, cliente, monkeypatch):
    monkeypatch.setattr(settings, "tracking_mock", False)
    cid = _criar_cliente(client, cliente)
    _, oid = _pedido(client, cliente, cid)
    assert client.get(f"/orders/{oid}/tracking", headers=cliente).status_code == 503


def test_cors_nao_ativo_por_padrao(client):
    r = client.options("/orders", headers={"Origin": "https://x.com", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in r.headers
