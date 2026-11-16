# SIG-Log Customer — CRM, SAC & Portal do Cliente (Squad 06)

Módulo da plataforma SIG-Log (Análise de Sistemas II). Porta de entrada da plataforma: cotação, pedidos, rastreamento, SAC, sinistros e avaliação.

## Rodar localmente
```bash
cp .env.example .env
docker compose up -d --build
```
| Serviço | URL |
|---|---|
| API (docs Swagger) | http://localhost:8000/docs |
| Health / Métricas | http://localhost:8000/health · /metrics |
| RabbitMQ (UI) | http://localhost:15672 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Jaeger | http://localhost:16686 |

## Desenvolvimento
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check . && pytest
```

## Stack
Python 3.12 + FastAPI · PostgreSQL (local / Supabase) · RabbitMQ · Docker Compose · GitHub Actions + GHCR · OpenTelemetry, Prometheus, Grafana, Jaeger · Trivy, SonarCloud, K6.

## Documentação
Progresso e pendências: [docs/00_checklist.md](docs/00_checklist.md)

## Segurança
Nunca versione `.env` ou credenciais. Segredos de CI ficam em *GitHub Secrets*. Use apenas dados fictícios.
