"""ACL para o squad Tracking: traduz o modelo deles para a visão do cliente.

PENDENTE DE ALINHAMENTO: o formato abaixo é uma SUPOSIÇÃO até o OpenAPI do Tracking ser publicado.
Esperado: GET {base}/tracking/orders/{order_id} -> {"status": "...", "events": [{"timestamp","description","location"}]}
"""
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
    }
