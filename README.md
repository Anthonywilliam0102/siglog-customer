# SIG-Log Customer — CRM, SAC & Portal do Cliente (Squad 06)

Módulo da plataforma SIG-Log (Análise de Sistemas II). Porta de entrada da plataforma: cotação, pedidos, rastreamento, SAC, sinistros e avaliação.

## Rodar localmente
```bash
cp .env.example .env
docker compose up -d --build
```
| Serviço | URL |
|---|---|
| API (Swagger)  | http://localhost:8000/docs |
| Health / Métricas | http://localhost:8000/health · /metrics |
| RabbitMQ (UI) | http://localhost:15672 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Jaeger | http://localhost:16686 |
| Portal (dev) | http://localhost:5173 |

## Testar a API localmente
```bash
export JWT_SECRET=$(grep JWT_SECRET .env | cut -d= -f2)
TOKEN=$(python scripts/gen_token.py meu-usuario cliente)   # perfis: cliente | atendente | gestor
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/docs
```
O Compose sobe também `migrate` (Alembic) e `worker` (publica eventos do Outbox no RabbitMQ).
Contrato: [openapi.yaml](openapi.yaml) · Eventos: [docs/08_events.md](docs/08_events.md)

## Front-end (`frontend/`)
```bash
cd frontend && npm install && npm run dev   # http://localhost:5173 (proxy /api -> :8000)
```

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
