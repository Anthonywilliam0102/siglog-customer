# Arquitetura

Microsserviço em camadas (Project Kit §4):

```
API (FastAPI/OpenAPI) -> Application (casos de uso/DTOs) -> Domain (entidades/regras/eventos)
                                   |
                         Infrastructure (PostgreSQL, RabbitMQ, clients externos)
Observability transversal: logs JSON, métricas Prometheus, traces OTel
```

| Camada | Pasta | Responsabilidade |
|---|---|---|
| API | `src/api` | rotas, validação, auth, OpenAPI |
| Application | `src/application` | casos de uso UC01–UC10, orquestração |
| Domain | `src/domain` | entidades, regras RN01–RN06, eventos (sem dependência de framework) |
| Infrastructure | `src/infrastructure` | repositórios SQLAlchemy, outbox, publisher RabbitMQ, ACL Tracking |
| Config | `src/config` | settings por ambiente |

**Padrões:** Repository, Outbox (publicação confiável), Idempotent Consumer, ACL, Dependency Injection.

**Implantação:** `docker compose` local (api, postgres, rabbitmq, prometheus, grafana, jaeger). Demo opcional: banco no Supabase; API exposta via Cloudflare Tunnel; front no Cloudflare Pages.
