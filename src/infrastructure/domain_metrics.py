"""Métricas de domínio para o dashboard Grafana (clientes, tickets, sinistros, SLA, satisfação).

Coletadas no scrape consultando o banco; se o banco falhar, o coletor não derruba o /metrics.
"""
import logging

from prometheus_client.core import GaugeMetricFamily
from sqlalchemy import func, select

from src.domain.rules import utcnow
from src.infrastructure import models as m

log = logging.getLogger(__name__)


class DomainCollector:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def collect(self):
        try:
            with self._session_factory() as s:
                clientes = s.scalar(select(func.count(m.Customer.id))) or 0
                por_status = dict(s.execute(select(m.Ticket.status, func.count()).group_by(m.Ticket.status)).all())
                vencidos = s.scalar(select(func.count(m.Ticket.id)).where(
                    m.Ticket.status != "RESOLVIDO", m.Ticket.sla_due_at < utcnow())) or 0
                sinistros = dict(s.execute(select(m.Claim.status, func.count()).group_by(m.Claim.status)).all())
                media = s.scalar(select(func.avg(m.Feedback.nota)))
                avaliacoes = s.scalar(select(func.count(m.Feedback.id))) or 0
        except Exception:  # noqa: BLE001 - métricas nunca devem quebrar o scrape
            log.warning("domain_metrics_unavailable")
            return

        g = GaugeMetricFamily("siglog_customers", "Clientes cadastrados")
        g.add_metric([], clientes)
        yield g
        g = GaugeMetricFamily("siglog_tickets", "Tickets por status", labels=["status"])
        for k, v in por_status.items():
            g.add_metric([k], v)
        yield g
        g = GaugeMetricFamily("siglog_tickets_sla_breached", "Tickets abertos com SLA vencido")
        g.add_metric([], vencidos)
        yield g
        g = GaugeMetricFamily("siglog_claims", "Sinistros por status", labels=["status"])
        for k, v in sinistros.items():
            g.add_metric([k], v)
        yield g
        g = GaugeMetricFamily("siglog_satisfaction_avg", "Nota média das avaliações (1-5)")
        g.add_metric([], float(media) if media is not None else 0.0)
        yield g
        g = GaugeMetricFamily("siglog_feedback_total", "Total de avaliações")
        g.add_metric([], avaliacoes)
        yield g
