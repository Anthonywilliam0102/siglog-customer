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
- [x] Matriz CSD (rascunho em `docs/16_ux_csd_empatia.md`) — 👤 validar com usuários
- [x] docs/03_personas.md — rascunho, 👤 validar com pesquisa
- [x] Mapa de Empatia (rascunho em `docs/16_ux_csd_empatia.md`) — 👤 validar com usuários
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
- [x] Código preparado para o Supabase (SSL, pooler, RLS 0002, tokens ES256/HS256) — `docs/15_supabase.md`
- [x] Projeto Supabase criado (região São Paulo, Data API desligada); `DATABASE_URL` e `SUPABASE_URL` só no `.env`
- [x] Validado no Supabase (VS Code, 23/11): JWKS `ES256`; `migrate` até `0002`; 9 tabelas com RLS e sem policies; login real de cliente e atendente; `POST /customers` 201; `GET /customers/{id}` 200/200/401; RN02 → 403 (com token de dev)
- [ ] 👤 (opcional, para a demo) criar `cliente2@exemplo.com` no Supabase e provar o 403 com login real
- [ ] 👤 Criar o usuário atendente de verdade no padrão da equipe (hoje é `atendimento@exemplo.com`, com perfil `atendente`)
- [x] UC01–UC10 implementados (API + regras RN01–RN06)
- [x] Publicação de eventos via Outbox + worker RabbitMQ (testado com publisher falso; 👤 validar com RabbitMQ real via Docker)
- [x] Testes unitários, integração e contrato (67 testes, SQLite)
- [ ] Testes de integração contra PostgreSQL e RabbitMQ reais (CI com services)
- [x] Autenticação JWT + papéis (docs/11_security.md)
- [ ] Consumidor de eventos do Tracking (status do pedido) — depende de contrato do outro squad
- [x] Esqueleto do front em `frontend/` (Vite + React; cotação e pedido) — 👤 Front evolui conforme o Figma
- [x] API: `GET /me` e listagens (`/customers`, `/orders`, `/tickets`, `/claims`) com RN02, filtros e paginação (47 testes)
- [x] Front completo em `frontend/`: login (Supabase Auth), cadastro, cotação/pedido, pedidos com rastreamento e avaliação, SAC com SLA, sinistros e fila do atendente. Testado ponta a ponta no navegador (21 verificações, cliente e atendente, desktop e celular)
- [x] Rastreamento simulado (`TRACKING_MOCK`) e CORS configurável (`CORS_ORIGINS`) — 50 testes
- [ ] 👤 Preencher `frontend/.env.local` com `VITE_SUPABASE_URL` e `VITE_SUPABASE_PUBLISHABLE_KEY` e validar o login real no navegador
- [ ] 👤 Ligar `TRACKING_MOCK=true` no `.env` para a demo mostrar rastreamento (o `.env.example` já traz)
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

## Validação no Docker (VS Code, 23/11)
- [x] Build, migrate (0001, 9 tabelas), Postgres, RabbitMQ, Prometheus, Grafana e Jaeger no ar
- [x] Fluxo cliente → cotação → pedido, RN02 (403) e RN07 (422) confirmados; Outbox publicou 3 eventos no exchange `siglog.events`
- [x] Corrigido: `httpx` movido para `requirements.txt` (a API caía em loop na imagem); worker com retry na conexão inicial; smoke test da imagem no CI
- [ ] 👤 Reconstruir (`docker compose up -d --build`) e conferir API *healthy*, alvo do Prometheus *up* e dashboard do Grafana (login `admin` / `GRAFANA_ADMIN_PASSWORD` do `.env`, padrão `admin_dev`)
- [ ] Criar fila ligada ao exchange para provar a entrega dos eventos (hoje só há publicação)
- [x] Reconstruído com o `httpx` corrigido: API *healthy*, Prometheus com api e worker *up*, 6 eventos do Outbox publicados; `ruff` e 33 testes passando (Python 3.12)
- [x] Jaeger: serviço `siglog-customer` com 20 traces (POST /customers, /quotes, /orders, GET, spans de banco) — confirmado no VS Code
- [x] Grafana: login, datasource e dashboard provisionados; 9 de 12 painéis com dados (os 3 vazios por falta de tráfego, ver abaixo)
- [ ] 👤 Gerar tickets, sinistros e avaliações e conferir os painéis *Tickets por status*, *Sinistros por status*, *Satisfação média*
- [ ] 👤 Validar o retry do worker numa subida a frio (`docker compose down && up`) e criar uma fila ligada ao exchange para provar a entrega dos eventos
- [ ] Worker sem tracing: o trace não atravessa API → worker (propagar `traceparent` no evento) — melhoria, não bloqueia o Demoday
- Nota: *Disponibilidade* usa `avg_over_time(up[5m])`; cai abaixo de 1 quando a API reinicia dentro da janela (ex.: rebuild)

## Publicação e entrega (Demoday 30/11)
- [x] Correção do 401 intermitente após o login: tolerância de relógio de 30 s no JWT (causa provável: `iat` no futuro por relógio do container), motivo da falha no log e nova tentativa no front antes de deslogar — 54 testes
- [x] Teste ponta a ponta do portal em `tests/e2e/` (17 verificações; modo Supabase ou dev)
- [x] Configuração de publicação: `render.yaml`, `Dockerfile` com `PORT`, `scripts/start.sh`, `frontend/public/_redirects` e guia `docs/18_publicacao.md`
- [x] E2E contra o Supabase real: 16/16 OK; `/me` 200 em 200 chamadas após 10 logins, sem `auth_failed` (VS Code, `8b299db`)
- [x] **Corrigido bug no Windows:** `scripts/start.sh` chegava com CRLF na imagem e a API caía em loop (`set: Illegal option -`). Correção: `.gitattributes` (`*.sh eol=lf`), `sed` no Dockerfile e passo no CI que simula o checkout do Windows
- [x] Redesenho do portal: login com painel de marca, hero, vidro (glassmorphism) nas superfícies de destaque, estatísticas, ícones, hover/foco, linha do tempo do pedido, skeleton, tema escuro e celular. E2E 17/17 após o redesenho
- [ ] 👤 Reconstruir (`docker compose ... up -d --build`) e confirmar que a API sobe sem o contorno de CRLF; conferir o visual novo no navegador
- [ ] 👤 Publicar a API no Render e o front no Cloudflare Pages (`docs/18_publicacao.md`) e testar a URL pública
- [x] PR #1 mergeado na `main` (commit `600be1b`); CI e publicação da imagem no GHCR passaram
- [x] Script de entrega `scripts/exportar_para_professor.sh` e guia `docs/19_entrega_professor.md` (fork + PR)
- [ ] 👤 Entregar ao repositório do professor (fork, pasta do squad, Pull Request) — falta a URL e o padrão de pasta do professor

## Integração entre squads e publicação (27/11)
- [x] Estrutura `contracts/` (entregamos em `provided/`, recebemos em `consumed/<squad>/`) e guia `docs/20_integracao_squads.md`
- [x] Contratos dos nossos eventos gerados do código (JSON Schema, exemplos, AsyncAPI) e testados: os eventos realmente emitidos validam contra os schemas
- [x] Proposta de contrato do Tracking + mock Prism (`docker-compose.integracao.yml`) + teste de contrato da nossa ACL
- [x] Consumidor de exemplo `scripts/consumir_eventos.py` para os outros squads e para provar a entrega no RabbitMQ
- [x] **CI corrigido:** rodava só `tests/unit` (27 de 67 testes); agora roda a suíte inteira (cobertura 94%) e valida os contratos recebidos
- [x] Publicação do front no GitHub Pages (`pages.yml`, subcaminho, variáveis) e `scripts/seed_demo.py` (dados de demonstração)
- [ ] 👤 Pedir os contratos aos squads 01, 02, 03, 04 e 05 (mensagem pronta em `docs/20`, seção 4) e combinar RabbitMQ compartilhado
- [ ] 👤 Rodar `scripts/consumir_eventos.py` contra o RabbitMQ e criar um pedido, para provar a entrega dos eventos
- [x] Modo demonstração do portal (API simulada no navegador, faixa de aviso) publicado pelo GitHub Pages quando faltam as variáveis; E2E 16/16 em modo demo e 17/17 em modo real
- [x] GitHub Pages habilitado e publicado (27/11)
- [x] **Sistema real no ar (27/11):** API no Render (`https://siglog-customer-api.onrender.com`, `/health` e `/docs` conferidos), variáveis do Pages criadas e site real em `https://anthonywilliam0102.github.io/siglog-customer/`, com Supabase
- [ ] 👤 Popular o banco da demo: `scripts/seed_demo.py --sim`

## Rodada de ajustes do front (27/11)
- [x] Login em tela cheia (rota ao fundo, cartão de vidro), abas **Entrar | Criar conta**, selo da equipe **Student Help** no rodapé
- [x] Botão Voltar, avisos (toasts), confirmação antes de cancelar pedido, arrastar para rolar tabelas e menu, ícones no menu
- [x] **Configurações** (equipe): URL da API por navegador + integrações com os outros squads (chave cifrada no servidor, nunca devolvida); migração 0003; 80 testes
- [x] E2E: 23/23 no modo demonstração e 22/22 no modo real
- [x] Login social no front (Google e GitHub, só aparecem os provedores ligados em `VITE_AUTH_PROVIDERS`); Apple descartada (US$ 99/ano)
- [x] GitHub ligado no Supabase (OAuth App, URL Configuration) e `VITE_AUTH_PROVIDERS=github`
- [x] Front também no **Cloudflare Pages** (`https://siglog-customer.pages.dev`), ligado ao GitHub; endereço principal para o professor
- [ ] 👤 Conferir no site novo o login com GitHub e o criar conta (Redirect URL do Supabase: `https://siglog-customer.pages.dev/**`)
- [ ] 👤 (opcional) Google no login: 15 min, `docs/15_supabase.md` 4.2
- [x] Supabase: Confirm email desligado, inscrição e provedor Email ligados (conferido por print)
- [x] **Verificado pelo usuário no site real (27/11):** login com GitHub, criar conta com e-mail e senha, e Configurações → Integrações (confirma a migração 0003 no Supabase)
- [ ] (obsoleto) Supabase: Confirm email desligado (e inscrição liberada) para o professor criar conta com e-mail fictício (`docs/15_supabase.md`, seção 4.1)
- [x] PR #3 mergeado; o Render aplicou a migração 0003 no Supabase

## Fase 5 — Integração e Demoday (Encontros 15–16)
- [x] Painéis de WMS e Financeiro no detalhe do pedido (via API configurável; simulados sem URL) e página **Integrações** no menu da conta, com Testar conexão (27/11; 87 testes; E2E demo 31/31 e real 30/30). Contratos de WMS/Financeiro são PROPOSTA, NÃO VERIFICADO com os squads
- [x] Integrações com uma aba por squad (campo de chave de API em todas), aba **Nossa API** (chaves emitidas por nós, só leitura de pedidos, hash no banco, migração 0004) (27/11)
- [x] **Fale conosco**: botão flutuante com headset, assistente automático (regras fixas, com dados reais do pedido) e chat do chamado com resposta automática de recebimento e atualização a cada 8 s
- [x] Origem/destino com lista das 27 capitais (filtra ao digitar; aceita outra cidade)
- [x] **Validação local (27/11, Claude do VS Code):** migrações até 0004, Nossa API (200/401/revogação), eventos no RabbitMQ sem duplicar, traces no Jaeger. **K6 FALHOU:** com 500 req/s o pool de conexões (5+10, espera de 30 s) esgotou e a API travou. Correção (27/11): pool configurável (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`=5 s) e resposta **503 + Retry-After** quando não há conexão livre. 👤 Refazer o K6 contra o banco LOCAL (não o Supabase) e registrar em `docs/13_load_test.md`
- [ ] 👤 Pendências da validação: painel de pedidos no Grafana (não existe), E2E no Supabase (decisão do usuário), compose puro apontando para o Supabase por causa do `.env` local
- [ ] Consumo de eventos (WMS e Financeiro) — depende dos contratos oficiais
- [ ] Release Candidate (congelamento)
- [ ] Release v1.0.0 (tag)
- [ ] README final
- [x] Deck do Demoday (artefato Claude, 11 slides) — 👤 revisar, preencher nomes e resultados do K6
- [x] docs/14_demoday_roteiro.md (roteiro e checklist de ensaio)
