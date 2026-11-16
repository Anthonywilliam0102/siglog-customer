# Contrato de API

O contrato oficial é o **[openapi.yaml](../openapi.yaml)** (gerado do código com `python scripts/export_openapi.py`). Swagger interativo em `/docs`.

| UC | Método e rota | Perfis |
|---|---|---|
| UC01 | `POST /customers` · `GET /customers/{id}` | todos autenticados |
| UC02 | `POST /quotes` | cliente (próprio), equipe |
| UC03 | `POST /orders` | cliente (próprio), equipe |
| UC04 | `GET /orders/{id}` | dono, equipe |
| UC05 | `GET /orders/{id}/tracking` | dono, equipe (depende do Tracking) |
| — | `PATCH /orders/{id}/status` | equipe (provisório até o consumidor de eventos do Tracking) |
| UC06 | `POST /tickets` · `GET /tickets/{id}` · `POST /tickets/{id}/messages` | dono, equipe |
| — | `PATCH /tickets/{id}/status` | equipe |
| UC07/08 | `POST /claims` · `GET /claims/{id}` | dono, equipe |
| UC09/10 | `POST /feedback` (`target`: ENTREGA \| ATENDIMENTO) | dono, equipe |
| infra | `GET /health` · `GET /metrics` | público (restringir em produção) |

**Erros:** 401 sem/ token inválido · 403 acesso negado (RN02) · 404 não encontrado · 409 conflito (documento duplicado, cotação já usada, avaliação repetida) · 422 validação/regra de negócio · 503 dependência (Tracking) indisponível.

**Regra de integração:** consumir APIs de outros squads apenas conforme o OpenAPI publicado por eles (testes de contrato em `tests/contract/`).
