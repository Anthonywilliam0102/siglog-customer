"""Contratos (JSON Schema) dos eventos que ESTE squad publica. Fonte única: `scripts/gerar_contratos.py` gera
`contracts/provided/` a partir daqui, e os testes garantem que o código só publica eventos válidos.
"""
from src.domain.events import PRODUCER, ROUTING_KEYS

UUID = {"type": "string", "format": "uuid"}
DECIMAL = {"type": "string", "pattern": r"^\d+(\.\d+)?$", "description": "valor monetário como texto decimal (ex.: \"290.40\")"}


def _obj(props: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": props, "required": required or list(props), "additionalProperties": False}


DATA = {
    "CotacaoSolicitada": _obj({"cotacao_id": UUID, "cliente_id": UUID, "origem": {"type": "string"}, "destino": {"type": "string"},
                               "peso_kg": {"type": "number"}, "volume_m3": {"type": "number"}}),
    "PedidoCriado": _obj({"pedido_id": UUID, "cliente_id": UUID, "cotacao_id": UUID, "origem": {"type": "string"}, "destino": {"type": "string"},
                          "carga": _obj({"peso_kg": {"type": "number"}, "volume_m3": {"type": "number"}}), "valor_estimado": DECIMAL}),
    "ChamadoAberto": _obj({"ticket_id": UUID, "cliente_id": UUID, "pedido_id": {"type": ["string", "null"], "format": "uuid"},
                           "categoria": {"type": "string"}, "prioridade": {"enum": ["ALTA", "MEDIA", "BAIXA"]}}),
    "SinistroRegistrado": _obj({"sinistro_id": UUID, "pedido_id": UUID, "cliente_id": UUID, "tipo": {"type": "string"}, "valor_reclamado": DECIMAL}),
    "EntregaAvaliada": _obj({"pedido_id": UUID, "cliente_id": UUID, "nota": {"type": "integer", "minimum": 1, "maximum": 5}}),
    "ClienteNotificado": _obj({"cliente_id": UUID, "canal": {"type": "string"}, "motivo": {"type": "string"}}),
}

DESCRICAO = {
    "CotacaoSolicitada": "Cliente pediu uma cotação. Consumidor típico: Financeiro (opcional).",
    "PedidoCriado": "Pedido criado a partir de uma cotação válida. Consumidores: WMS (iniciar separação) e Financeiro (frete e cobrança).",
    "ChamadoAberto": "Chamado de atendimento aberto no SAC (indicadores).",
    "SinistroRegistrado": "Avaria, extravio ou ocorrência registrada. Consumidor: Financeiro (estorno e indenização).",
    "EntregaAvaliada": "Cliente avaliou a entrega (indicadores de Frota e Tracking).",
    "ClienteNotificado": "Notificação enviada ao cliente (auditoria).",
}

EXEMPLOS_DATA = {
    "CotacaoSolicitada": {"cotacao_id": "3f6c8f0e-6b1d-4c2a-9a55-1a2b3c4d5e61", "cliente_id": "b2852258-1c3d-4e5f-8a9b-0c1d2e3f4a5b",
                          "origem": "São Paulo/SP", "destino": "Recife/PE", "peso_kg": 120.5, "volume_m3": 1.2},
    "PedidoCriado": {"pedido_id": "6d2331ec-0a1b-4c2d-8e3f-4a5b6c7d8e9f", "cliente_id": "b2852258-1c3d-4e5f-8a9b-0c1d2e3f4a5b",
                     "cotacao_id": "3f6c8f0e-6b1d-4c2a-9a55-1a2b3c4d5e61", "origem": "São Paulo/SP", "destino": "Recife/PE",
                     "carga": {"peso_kg": 120.5, "volume_m3": 1.2}, "valor_estimado": "290.40"},
    "ChamadoAberto": {"ticket_id": "5a4a428f-9b8c-4d7e-a6f5-1e2d3c4b5a69", "cliente_id": "b2852258-1c3d-4e5f-8a9b-0c1d2e3f4a5b",
                      "pedido_id": "6d2331ec-0a1b-4c2d-8e3f-4a5b6c7d8e9f", "categoria": "ATRASO", "prioridade": "ALTA"},
    "SinistroRegistrado": {"sinistro_id": "7b8c9d0e-1f2a-4b3c-8d4e-5f6a7b8c9d0e", "pedido_id": "6d2331ec-0a1b-4c2d-8e3f-4a5b6c7d8e9f",
                           "cliente_id": "b2852258-1c3d-4e5f-8a9b-0c1d2e3f4a5b", "tipo": "AVARIA", "valor_reclamado": "180.00"},
    "EntregaAvaliada": {"pedido_id": "6d2331ec-0a1b-4c2d-8e3f-4a5b6c7d8e9f", "cliente_id": "b2852258-1c3d-4e5f-8a9b-0c1d2e3f4a5b", "nota": 5},
    "ClienteNotificado": {"cliente_id": "b2852258-1c3d-4e5f-8a9b-0c1d2e3f4a5b", "canal": "email", "motivo": "pedido EM_TRANSPORTE"},
}


def envelope_schema(event_type: str) -> dict:
    """Schema completo da mensagem (envelope + `data`) de um evento."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://siglog.local/contracts/customer/{event_type}.schema.json",
        "title": event_type,
        "description": DESCRICAO[event_type],
        "type": "object",
        "required": ["event_id", "event_type", "version", "occurred_at", "producer", "correlation_id", "data"],
        "additionalProperties": False,
        "properties": {
            "event_id": {**UUID, "description": "Identificador único. Consumidores devem deduplicar por este campo (entrega at-least-once)."},
            "event_type": {"const": event_type},
            "version": {"const": 1},
            "occurred_at": {"type": "string", "format": "date-time"},
            "producer": {"const": PRODUCER},
            "correlation_id": {**UUID, "description": "Propague nos seus eventos/logs para rastrear o fluxo entre squads."},
            "data": DATA[event_type],
        },
    }


def exemplo(event_type: str) -> dict:
    return {"event_id": "0b1c2d3e-4f5a-4b6c-8d7e-9f0a1b2c3d4e", "event_type": event_type, "version": 1,
            "occurred_at": "2026-11-27T12:00:00+00:00", "producer": PRODUCER,
            "correlation_id": "9e8d7c6b-5a4f-4e3d-8c2b-1a0f9e8d7c6b", "data": EXEMPLOS_DATA[event_type]}


def asyncapi() -> dict:
    canais = {}
    for tipo, chave in ROUTING_KEYS.items():
        canais[chave] = {"description": DESCRICAO[tipo], "subscribe": {"operationId": f"consumir{tipo}", "message": {
            "name": tipo, "contentType": "application/json", "payload": envelope_schema(tipo)}}}
    return {
        "asyncapi": "2.6.0",
        "info": {"title": "SIG-Log Customer — eventos publicados", "version": "1.0.0",
                 "description": "Exchange topic `siglog.events` (durável). Entrega at-least-once via Outbox: deduplique por `event_id`."},
        "servers": {"broker": {"url": "${RABBITMQ_URL}", "protocol": "amqp", "description": "RabbitMQ compartilhado entre os squads"}},
        "channels": canais,
    }
