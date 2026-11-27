"""Gera monitoring/grafana/dashboards/siglog-customer.json (rode após mudar painéis)."""
import json
from pathlib import Path

panels = []


def panel(title, expr, x, y, kind="timeseries", unit=None, w=6, legend=None):
    p = {
        "id": len(panels) + 1, "title": title, "type": kind, "datasource": "Prometheus",
        "gridPos": {"x": x, "y": y, "w": w, "h": 7},
        "targets": [{"expr": expr, "refId": "A", "legendFormat": legend or ""}],
        "fieldConfig": {"defaults": {"unit": unit} if unit else {}, "overrides": []},
    }
    panels.append(p)


def row(title, y):
    panels.append({"id": len(panels) + 1, "title": title, "type": "row", "collapsed": False,
                   "gridPos": {"x": 0, "y": y, "w": 24, "h": 1}})


row("Operacional (comum a todos os módulos)", 0)
panel("Requests/min", 'sum(rate(requests_total[1m])) * 60', 0, 1, unit="reqpm")
panel("Latência p95", 'histogram_quantile(0.95, sum(rate(request_duration_bucket[5m])) by (le))', 6, 1, unit="s")
panel("Taxa de erros (5xx)", 'sum(rate(errors_total[5m])) / clamp_min(sum(rate(requests_total[5m])), 1)', 12, 1,
      unit="percentunit")
panel("Disponibilidade", 'avg_over_time(up{job="siglog-customer"}[5m])', 18, 1, kind="stat", unit="percentunit")
panel("Mensagens processadas", 'sum(rate(messages_processed_total[5m])) * 60', 0, 8, unit="cpm", w=12)
panel("Requisições ativas", 'active_requests', 12, 8, w=12)

row("Domínio: clientes, tickets, sinistros, SLA, satisfação", 15)
panel("Clientes", 'siglog_customers', 0, 16, kind="stat")
panel("Tickets por status", 'siglog_tickets', 6, 16, legend="{{status}}")
panel("Tickets com SLA vencido", 'siglog_tickets_sla_breached', 12, 16, kind="stat")
panel("Sinistros por status", 'siglog_claims', 18, 16, legend="{{status}}")
panel("Satisfação média (1–5)", 'siglog_satisfaction_avg', 0, 23, kind="gauge", w=12)
panel("Total de avaliações", 'siglog_feedback_total', 12, 23, kind="stat", w=12)

dash = {"uid": "siglog-customer", "title": "SIG-Log Customer", "schemaVersion": 39, "version": 1,
        "refresh": "10s", "time": {"from": "now-1h", "to": "now"}, "panels": panels, "tags": ["siglog"]}
Path("monitoring/grafana/dashboards/siglog-customer.json").write_text(json.dumps(dash, indent=2, ensure_ascii=False))
print("ok")
