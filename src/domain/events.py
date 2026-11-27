"""Envelope e catálogo de eventos publicados (ver docs/08_events.md)."""
import uuid
from datetime import datetime, timezone

PRODUCER = "siglog-customer"

ROUTING_KEYS = {
    "CotacaoSolicitada": "customer.cotacao.solicitada",
    "PedidoCriado": "customer.pedido.criado",
    "ChamadoAberto": "customer.chamado.aberto",
    "SinistroRegistrado": "customer.sinistro.registrado",
    "EntregaAvaliada": "customer.entrega.avaliada",
    "ClienteNotificado": "customer.cliente.notificado",
}


def envelope(event_type: str, data: dict, correlation_id: str | None = None) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "version": 1,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "producer": PRODUCER,
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "data": data,
    }
