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
- [x] docs/01_product_vision.md (Project Charter) — rascunho, 👤 UI/UX revisar
- [ ] 👤 Matriz CSD (UI/UX)
- [x] docs/03_personas.md — rascunho, 👤 validar com pesquisa
- [ ] 👤 Mapa de Empatia (UI/UX)
- [ ] 👤 Protótipo Figma + teste de usabilidade (UI/UX)
- [x] docs/02_requirements.md (RF, RNF, regras de negócio)

## Fase 2 — DDD e contratos (Encontros 3–6, Marco 1)
- [x] Event Storming (resumo em docs/04_ddd.md) — 👤 fazer a sessão visual com o time
- [x] docs/04_ddd.md (agregados, comandos, eventos)
- [x] Bounded Context + docs/05_context_map.md
- [x] docs/06_architecture.md
- [x] openapi.yaml (gerado do código)
- [x] docs/08_events.md (catálogo) — eventos consumidos PENDENTES de alinhamento
- [x] ADR-001..005 (docs/adr/)
- [ ] 👤 Obter OpenAPI/Event Catalog dos outros squads e alinhar broker RabbitMQ

## Fase 3 — Código, banco, mensageria (Encontros 7–10, Marco 2)
- [x] Modelo de dados + migração Alembic 0001 (docs/09_database.md)
- [ ] 👤 Projeto Supabase criado (pessoa do banco); credenciais só em .env / GitHub Secrets
- [x] UC01–UC10 implementados (API + regras RN01–RN06)
- [x] Publicação de eventos via Outbox + worker RabbitMQ (testado com publisher falso; 👤 validar com RabbitMQ real via Docker)
- [x] Testes unitários, integração e contrato (33 testes, SQLite)
- [ ] Testes de integração contra PostgreSQL e RabbitMQ reais (CI com services)
- [x] Autenticação JWT + papéis (docs/11_security.md)
- [ ] Consumidor de eventos do Tracking (status do pedido) — depende de contrato do outro squad
- [x] Esqueleto do front em `frontend/` (Vite + React; cotação e pedido) — 👤 Front evolui conforme o Figma
- [ ] 👤 Front: telas de SAC, sinistro, rastreamento, avaliação e login (Supabase Auth)
- [ ] 👤 Deploy do front no Cloudflare Pages (build: `npm run build`, diretório `frontend`, saída `dist`, var `VITE_API_URL`)

## Fase 4 — Observabilidade, segurança, carga (Encontros 11–14)
- [x] OpenTelemetry (traces → Jaeger) — docs/10_observability.md (👤 conferir traces no Jaeger com Docker)
- [x] Dashboard Grafana (geral + domínio) provisionado automaticamente — 👤 conferir visualmente com Docker
- [ ] 👤 SonarCloud: criar projeto e secret SONAR_TOKEN; ativar job no CI
- [ ] Trivy bloqueante (exit-code 1)
- [x] Script K6 pronto (tests/load/k6.js)
- [ ] 👤 Executar K6 e preencher resultados em docs/13_load_test.md
- [x] docs/12_atam.md (4 cenários)

## Revisão do PR #1
- [x] 9 achados do code-review corrigidos (commit antes da resposta, label de métricas, corrida 409, JWT com exp, worker resiliente, transições de status, CD após CI, portas em localhost, worker sem bloquear o loop)

## Fase 5 — Integração e Demoday (Encontros 15–16)
- [ ] Integração com WMS e Financeiro (eventos consumidos)
- [ ] Release Candidate (congelamento)
- [ ] Release v1.0.0 (tag)
- [ ] README final
- [x] Deck do Demoday (artefato Claude, 11 slides) — 👤 revisar, preencher nomes e resultados do K6
- [x] docs/14_demoday_roteiro.md (roteiro e checklist de ensaio)
