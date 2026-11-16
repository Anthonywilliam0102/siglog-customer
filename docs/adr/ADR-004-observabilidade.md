# ADR-004 — Estratégia de observabilidade
**Status:** Aceita (implementação parcial)

**Decisão:** Logs JSON estruturados, métricas Prometheus (`requests_total`, `request_duration`, `errors_total`, `active_requests`), traces OpenTelemetry → Jaeger, dashboards no Grafana.
**Justificativa:** padrão do Project Kit §8; ferramentas open source e gratuitas, todas em containers.
**Consequências:** custo de CPU/RAM no ambiente local; OpenTelemetry e dashboards específicos (clientes, tickets, sinistros, SLA, satisfação) ficam para a Fase 4.
