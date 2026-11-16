"""Garante que a API expõe os endpoints do Anexo A.6 do Project Kit."""
from fastapi.testclient import TestClient

from src.api.main import app

ESPERADOS = {
    ("post", "/customers"), ("post", "/quotes"), ("post", "/orders"),
    ("get", "/orders/{order_id}"), ("get", "/orders/{order_id}/tracking"),
    ("post", "/tickets"), ("post", "/claims"), ("post", "/feedback"),
}


def test_endpoints_do_anexo_a6_presentes():
    spec = TestClient(app).get("/openapi.json").json()
    presentes = {(met, path) for path, ops in spec["paths"].items() for met in ops}
    assert ESPERADOS <= presentes


def test_eventos_publicados_tem_routing_key():
    from src.domain.events import ROUTING_KEYS

    assert set(ROUTING_KEYS) == {"CotacaoSolicitada", "PedidoCriado", "ChamadoAberto",
                                 "SinistroRegistrado", "EntregaAvaliada", "ClienteNotificado"}
