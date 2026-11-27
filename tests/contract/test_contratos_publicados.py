"""O contrato publicado em `contracts/provided/` precisa ser exatamente o que o código produz e o que o serviço emite."""
import importlib.util
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from sqlalchemy import select

from src.api.main import app
from src.domain import event_contracts as ec
from src.domain.events import ROUTING_KEYS
from src.infrastructure import models as m
from tests.integration.test_fluxo_api import _criar_cliente, _pedido

RAIZ = Path(__file__).resolve().parents[2]
CHECKER = FormatChecker()


def _gerador():
    spec = importlib.util.spec_from_file_location("gerar_contratos", RAIZ / "scripts" / "gerar_contratos.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _validar(esquema, instancia):
    Draft202012Validator.check_schema(esquema)
    erros = list(Draft202012Validator(esquema, format_checker=CHECKER).iter_errors(instancia))
    assert not erros, [e.message for e in erros]


def test_exemplos_validam_contra_os_schemas():
    for tipo in ROUTING_KEYS:
        _validar(ec.envelope_schema(tipo), ec.exemplo(tipo))


def test_arquivos_versionados_estao_atualizados():
    """Se falhar: rode `python scripts/gerar_contratos.py` e commite o resultado."""
    for caminho, esperado in _gerador().arquivos().items():
        assert caminho.read_text(encoding="utf-8") == esperado, f"{caminho.relative_to(RAIZ)} desatualizado"


def test_openapi_versionado_esta_atualizado():
    atual = yaml.safe_dump(app.openapi(), allow_unicode=True, sort_keys=False)
    assert (RAIZ / "openapi.yaml").read_text(encoding="utf-8") == atual, "openapi.yaml desatualizado: rode scripts/gerar_contratos.py"


def test_eventos_realmente_emitidos_obedecem_ao_contrato(client, cliente, atendente, session_factory):
    cid = _criar_cliente(client, cliente)
    _, oid = _pedido(client, cliente, cid)
    client.post("/tickets", json={"customer_id": cid, "order_id": oid, "categoria": "ATRASO", "prioridade": "ALTA",
                                  "assunto": "Atraso", "mensagem": "Onde está?"}, headers=cliente)
    client.post("/claims", json={"order_id": oid, "tipo": "AVARIA", "descricao": "Caixa amassada", "valor_reclamado": "150.00"}, headers=cliente)
    for st in ("EM_SEPARACAO", "EM_TRANSPORTE", "ENTREGUE"):
        client.patch(f"/orders/{oid}/status", json={"status": st}, headers=atendente)
    client.post("/feedback", json={"target": "ENTREGA", "nota": 5, "order_id": oid}, headers=cliente)

    with session_factory() as s:
        emitidos = [e.payload for e in s.scalars(select(m.OutboxEvent))]
    assert {p["event_type"] for p in emitidos} == set(ROUTING_KEYS), "algum evento não foi emitido no fluxo"
    for payload in emitidos:
        _validar(ec.envelope_schema(payload["event_type"]), payload)


def test_asyncapi_tem_um_canal_por_evento():
    canais = yaml.safe_load((RAIZ / "contracts" / "provided" / "asyncapi.yaml").read_text(encoding="utf-8"))["channels"]
    assert set(canais) == set(ROUTING_KEYS.values())
    assert json.loads((RAIZ / "contracts" / "provided" / "events" / "PedidoCriado.schema.json").read_text(encoding="utf-8"))["title"] == "PedidoCriado"
