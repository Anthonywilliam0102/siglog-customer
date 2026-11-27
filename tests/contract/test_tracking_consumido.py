"""Nossa camada anticorrupção (ACL) contra o contrato do Tracking em `contracts/consumed/tracking/`.
Quando o squad 03 entregar o contrato oficial, este teste passa a validar a integração de verdade."""
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from src.config.settings import settings
from src.infrastructure.clients import tracking

ARQUIVO = Path(__file__).resolve().parents[2] / "contracts" / "consumed" / "tracking" / "openapi.yaml"
CONTRATO = yaml.safe_load(ARQUIVO.read_text(encoding="utf-8"))
RESP = CONTRATO["paths"]["/tracking/orders/{order_id}"]["get"]["responses"]["200"]["content"]["application/json"]
SCHEMA = {**CONTRATO["components"]["schemas"]["Rastreamento"], "$defs": {}}


class _Resposta:
    def __init__(self, corpo):
        self._c = corpo

    def raise_for_status(self):
        return None

    def json(self):
        return self._c


def test_exemplo_do_contrato_e_valido_pelo_proprio_schema():
    assert not list(Draft202012Validator(SCHEMA).iter_errors(RESP["example"]))


def test_acl_traduz_o_exemplo_do_contrato(monkeypatch):
    monkeypatch.setattr(settings, "tracking_base_url", "http://tracking.invalid")
    monkeypatch.setattr(tracking.httpx, "get", lambda url, timeout, **kw: _Resposta(RESP["example"]))
    r = tracking.fetch_tracking("6d2331ec-0a1b-4c2d-8e3f-4a5b6c7d8e9f")
    assert r["status"] == "Em trânsito" and len(r["events"]) == 2 and r["source"] == "tracking"


@pytest.mark.parametrize("status", CONTRATO["components"]["schemas"]["Rastreamento"]["properties"]["status"]["enum"])
def test_todo_status_do_contrato_tem_texto_para_o_cliente(status):
    assert status in tracking.STATUS_AMIGAVEL, f"status {status} do contrato sem tradução na ACL"


def test_url_chamada_segue_o_caminho_do_contrato(monkeypatch):
    chamadas = []
    monkeypatch.setattr(settings, "tracking_base_url", "http://tracking.invalid")
    monkeypatch.setattr(tracking.httpx, "get", lambda url, timeout, **kw: chamadas.append(url) or _Resposta(RESP["example"]))
    tracking.fetch_tracking("abc")
    assert chamadas == ["http://tracking.invalid/tracking/orders/abc"]
    assert "/tracking/orders/{order_id}" in CONTRATO["paths"]
