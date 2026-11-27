"""ACL para o squad Tracking: traduz o modelo deles para a visão do cliente.

PENDENTE DE ALINHAMENTO: o formato abaixo é uma SUPOSIÇÃO até o OpenAPI do Tracking ser publicado.
Esperado: GET {base}/tracking/orders/{order_id} -> {"status": "...", "events": [{"timestamp","description","location"}]}
"""
from datetime import timedelta

import httpx

from src.config.settings import settings
from src.domain.errors import DomainError

STATUS_AMIGAVEL = {
    "PICKED_UP": "Coletado",
    "IN_TRANSIT": "Em trânsito",
    "OUT_FOR_DELIVERY": "Saiu para entrega",
    "DELIVERED": "Entregue",
    "EXCEPTION": "Ocorrência na entrega",
}


class TrackingUnavailable(DomainError):
    status = 503


def fetch_tracking(order_id: str) -> dict:
    if not settings.tracking_base_url:
        raise TrackingUnavailable("Serviço de rastreamento não configurado")
    try:
        r = httpx.get(f"{settings.tracking_base_url}/tracking/orders/{order_id}", timeout=3.0)
        r.raise_for_status()
        raw = r.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise TrackingUnavailable("Serviço de rastreamento indisponível") from exc
    return {
        "order_id": order_id,
        "status": STATUS_AMIGAVEL.get(raw.get("status", ""), raw.get("status", "Desconhecido")),
        "events": raw.get("events", []),
        "source": "tracking",
    }


# --- MOCK (somente demo): gera o rastreamento a partir do status do pedido -------------------------
_MOCK_STEPS = [
    ("Coletado", "Coletado no centro de distribuição de {origem}"),
    ("Em trânsito", "Em trânsito entre {origem} e {destino}"),
    ("Saiu para entrega", "Saiu para entrega em {destino}"),
    ("Entregue", "Entregue ao destinatário em {destino}"),
]
_MOCK_DONE = {"CRIADO": 0, "EM_SEPARACAO": 0, "EM_TRANSPORTE": 2, "ENTREGUE": 4, "CANCELADO": 0}
_MOCK_WAITING = {"CRIADO": "Aguardando separação", "EM_SEPARACAO": "Em separação no CD", "CANCELADO": "Pedido cancelado"}


def mock_tracking(order) -> dict:
    status = str(order.status)
    done = _MOCK_DONE.get(status, 0)
    base = order.created_at
    events = [
        {"timestamp": (base + timedelta(hours=6 * (i + 1))).isoformat(), "description": text.format(
            origem=order.origem, destino=order.destino), "location": order.origem if i < 2 else order.destino}
        for i, (_, text) in enumerate(_MOCK_STEPS[:done])
    ]
    label = _MOCK_STEPS[done - 1][0] if done else _MOCK_WAITING.get(status, "Aguardando coleta")
    return {"order_id": str(order.id), "status": label, "events": events, "source": "mock"}
