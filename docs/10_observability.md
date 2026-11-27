# Observabilidade

| Pilar | Implementação | Onde ver |
|---|---|---|
| Logs | JSON estruturado (`timestamp, service, event, level`) em stdout | `docker compose logs api` |
| Métricas | `prometheus_client`: `requests_total`, `request_duration`, `errors_total`, `active_requests`; worker: `messages_processed_total`; domínio: `siglog_customers`, `siglog_tickets{status}`, `siglog_tickets_sla_breached`, `siglog_claims{status}`, `siglog_satisfaction_avg`, `siglog_feedback_total` | Prometheus :9090 |
| Traces | OpenTelemetry (FastAPI + SQLAlchemy) → OTLP/HTTP → Jaeger; ligado quando `OTEL_EXPORTER_OTLP_ENDPOINT` está definido | Jaeger :16686 |
| Dashboards | `monitoring/grafana/dashboards/siglog-customer.json` (provisionado automaticamente; gerado por `scripts/gen_dashboard.py`) | Grafana :3000 |

**Dashboard:** operacional (requests/min, latência p95, taxa de erros, disponibilidade, mensagens processadas) e de domínio (clientes, tickets, sinistros, SLA, satisfação).

**Observações**
- O label `path` das métricas usa o **template da rota** (`/orders/{order_id}`), não o path real, para não criar uma série por UUID.
- O worker do Outbox reinicia sozinho (`restart: unless-stopped`) e registra `outbox_error` sem derrubar o processo.
- Métricas de domínio são lidas do banco a cada scrape (15 s); simples e suficiente para o porte do projeto. Em escala, trocar por contadores incrementais.
- `/health` e `/metrics` não geram spans (evita ruído).
- O trace distribuído CRM → WMS → ... → Financeiro depende de propagar `traceparent` nos eventos/mensagens (PENDENTE, requer os demais squads).
