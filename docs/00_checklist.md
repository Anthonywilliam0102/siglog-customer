# Checklist do Projeto — SIG-Log Customer (Squad 06)

Legenda: [x] feito · [ ] pendente · 👤 depende de uma pessoa do squad · 🤖 conduzido pelo Claude

## Fase 0 — Esqueleto e infraestrutura local
- [x] Estrutura de pastas conforme Project Kit (seção 3)
- [x] Dockerfile (usuário não-root, healthcheck)
- [x] docker-compose.yml (api, postgres, rabbitmq, prometheus, grafana, jaeger)
- [x] API mínima (/health, /metrics) com logs JSON e métricas básicas
- [x] Teste unitário inicial + lint (ruff)
- [x] CI (lint, testes, docker build, Trivy) e CD (push para GHCR)
- [ ] 👤 Push inicial para o GitHub e conferir o CI verde
- [ ] 👤 Proteger a branch `main` (PR obrigatório) e criar `develop`
- [ ] 👤 Convidar os 3 colegas ao repositório

## Fase 1 — Produto e UX (Encontros 1–2) — UI/UX lidera
- [ ] docs/01_product_vision.md (Project Charter)
- [ ] Matriz CSD
- [ ] docs/03_personas.md
- [ ] Mapa de Empatia
- [ ] Protótipo Figma + teste de usabilidade
- [ ] docs/02_requirements.md (requisitos funcionais e não funcionais)

## Fase 2 — DDD e contratos (Encontros 3–6, Marco 1)
- [ ] Event Storming
- [ ] docs/04_ddd.md (agregados, comandos, eventos)
- [ ] Bounded Context + docs/05_context_map.md
- [ ] docs/06_architecture.md
- [ ] openapi.yaml (endpoints A.6)
- [ ] docs/08_events.md (catálogo: payload, produtor, consumidores)
- [ ] ADR-001..005 (pasta docs/adr/)
- [ ] 👤 Obter OpenAPI/Event Catalog dos outros squads e alinhar broker RabbitMQ

## Fase 3 — Código, banco, mensageria (Encontros 7–10, Marco 2)
- [ ] Modelo de dados + migrações Alembic (docs/09_database.md)
- [ ] 👤 Projeto Supabase criado (pessoa do banco); credenciais só em .env / GitHub Secrets
- [ ] UC01–UC10 implementados
- [ ] Publicação de eventos (PedidoCriado, SinistroRegistrado…)
- [ ] Testes unitários, integração e contrato
- [ ] Autenticação JWT + papéis (docs/11_security.md)

## Fase 4 — Observabilidade, segurança, carga (Encontros 11–14)
- [ ] OpenTelemetry (traces → Jaeger) — docs/10_observability.md
- [ ] Dashboard Grafana (geral + clientes, tickets, sinistros, SLA, satisfação)
- [ ] 👤 SonarCloud: criar projeto e secret SONAR_TOKEN; ativar job no CI
- [ ] Trivy bloqueante (exit-code 1)
- [ ] Teste de carga K6 (100/500/1000 req/s) — docs/13_load_test.md
- [ ] docs/12_atam.md (4 cenários)

## Fase 5 — Integração e Demoday (Encontros 15–16)
- [ ] Integração com WMS e Financeiro (eventos consumidos)
- [ ] Release Candidate (congelamento)
- [ ] Release v1.0.0 (tag)
- [ ] README final
- [ ] Deck do Demoday
