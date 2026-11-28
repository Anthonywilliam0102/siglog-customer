# SIG-Log Customer (Squad 06) — contexto para o Claude

Projeto **acadêmico** (Análise de Sistemas II): módulo CRM, SAC & Portal do Cliente da plataforma SIG-Log.
Equipe de 4: Banco, Back, Front, UI/UX. Use **somente dados fictícios**. Idioma: português (BR).
Fonte da verdade do escopo: Project Kit (encontros 1–16) e `docs/00_checklist.md` (progresso e pendências).

## Stack
Python 3.12 + FastAPI · SQLAlchemy 2.0 + Alembic · PostgreSQL (container; Supabase opcional na demo) · RabbitMQ (Outbox + worker) ·
Docker Compose · GitHub Actions (CI/CD, GHCR) · OpenTelemetry, Prometheus, Grafana, Jaeger · Trivy · K6 · front React + Vite em `frontend/`.

## Estrutura
`src/api` (rotas, auth, schemas) · `src/application` (casos de uso UC01–UC10) · `src/domain` (regras puras, eventos) ·
`src/infrastructure` (db, models, outbox, telemetria, clients/tracking) · `migrations/` (Alembic) · `tests/{unit,integration,contract,load}` ·
`monitoring/` · `docs/` (13 docs + `adr/`) · `openapi.yaml` (gerado: `python scripts/export_openapi.py`).

## Comandos
```bash
cp .env.example .env && docker compose up -d --build     # ambiente completo
docker compose ps -a ; docker compose logs api worker migrate --tail 40
python -m venv .venv && . .venv/Scripts/activate          # Git Bash no Windows (Linux/Mac: .venv/bin/activate)
pip install -r requirements-dev.txt && ruff check . && pytest
python scripts/gen_token.py <sub> <cliente|atendente|gestor> [horas]   # JWT de dev (exige JWT_SECRET igual ao .env)
python scripts/export_openapi.py ; python scripts/gen_dashboard.py     # regenerar contrato / dashboard Grafana
cd frontend && npm install && npm run dev
```

## Convenções e decisões que NÃO devem ser desfeitas sem conversar
- **Commit antes da resposta:** as rotas de escrita chamam `commit(session, ...)`. Não mover o commit para o teardown da dependência (roda depois da resposta).
- **Outbox:** eventos são gravados na mesma transação do negócio; o worker publica no RabbitMQ (exchange `siglog.events`). Consumidores devem ser idempotentes por `event_id`.
- **RN02:** cliente só acessa os próprios dados (`owner_sub`); atendente/gestor veem tudo. **RN07:** transições de status do pedido (CRIADO → EM_SEPARACAO → EM_TRANSPORTE → ENTREGUE; CANCELADO antes do transporte).
- **JWT** com `exp` e `sub` obrigatórios, tolerância de relógio de 30 s; HS256 (dev, só com `JWT_SECRET`) ou ES256 do Supabase (JWKS). Perfil de `app_metadata.role`. Na nuvem não definir `JWT_SECRET`.
- Métricas: label `path` é o **template da rota**. Portas do Compose só em `127.0.0.1`.
- **Demoday:** banco no **Supabase** (`docs/15_supabase.md`; rodar com `docker-compose.supabase.yml`), estrutura do projeto feita pelo Claude. Perfil do usuário só de `app_metadata.role`. Migração 0002 liga RLS: não remover.
- Banco: PostgreSQL (o enunciado exige). Cloudflare D1 (SQLite) foi descartado (ADR-002). Mudou modelo → nova migração Alembic, nunca editar a 0001.
- Mudou rotas/schemas → regenerar `openapi.yaml`. Mudou regra → atualizar `docs/` e testes.
- Segredos nunca no repositório (`.env` é ignorado; CI usa GitHub Secrets).

## Fluxo com dois Claudes (nuvem + VS Code)
- **Claude da nuvem (builder):** escreve código, testes, migrações, CI e documentação; mantém `docs/00_checklist.md`, `openapi.yaml` e este arquivo.
- **Claude do VS Code (executor local):** roda Docker, K6, Supabase e valida; **não edita código nem o checklist**. Registra o que verificou em `docs/validacao_local.md` (arquivo só dele, sempre adicionando no fim) e responde com o relatório em CONFIRMADO / NÃO VERIFICADO / FALHOU.
- **Antes de começar qualquer tarefa:** `git pull`. Se precisar corrigir algo no código, descreva o problema no relatório em vez de commitar (evita conflito e correção duplicada).
- **Segredos** (Supabase, senhas) ficam só no `.env` local e nunca vão para commit, chat ou relatório.
- **Próximo passo** sai sempre do checklist: o executor lê `docs/00_checklist.md` e executa os itens marcados com 👤 que dependem da máquina local.

## Git
Trabalho na branch `develop`; `main` recebe PR (PR #1 já mergeado em 27/11; novas mudanças entram por novo PR). Mensagens de commit em português, no formato `tipo: resumo`.
Não fazer push em `main`, merge, tag `v1.0.0` ou ações destrutivas sem confirmação do usuário.

## Estado atual (ver docs/00_checklist.md para o detalhe)
Feito: docs de produto/DDD/ADRs, API UC01–UC10, Outbox + worker, Alembic, OTel, dashboard Grafana, script K6, ATAM, esqueleto do front, deck do Demoday, 47 testes (SQLite) e CI verde.
Validado no Docker local (23/11): migrate, fluxo cliente→pedido, RN02/RN07 e publicação do Outbox. Corrigido `httpx` fora do requirements.txt (API caía na imagem).
Supabase validado (23/11): JWKS ES256, migrate 0002, RLS em 9 tabelas, login real (cliente/atendente) e RN02. API com `GET /me` e listagens. Front completo em `frontend/` (React + Router, login Supabase), testado no navegador. Demoday: **30/11**. 94 testes. Carga (K6 local): normal 100 req/s ok (p95 415 ms); pico degrada com 503 rápidas (limite de requisições em andamento, pool com timeout de 5 s); ver `docs/13_load_test.md`. Chamados: botão flutuante "Fale conosco" -> assistente automático (regras fixas) -> chamado; resposta automática author_role "sistema". Chaves de API emitidas por nós (tabela api_keys, migração 0004, X-API-Key só em GET /orders). Publicação: `docs/18_publicacao.md` (Render + Cloudflare Pages + plano B com túnel). Teste E2E: `tests/e2e/`. `.gitattributes` força LF em `*.sh`/Dockerfile (Windows gerava CRLF e quebrava o `start.sh`). Visual do portal: glassmorphism só em hero/login/estatísticas, tabelas e formulários em fundo sólido. **NO AR (27/11):** site principal `https://siglog-customer.pages.dev` (Cloudflare Pages, ligado ao GitHub: build `npm ci && npm run build`, raiz `frontend`, saída `dist`, mesmas variáveis `VITE_*`) e reserva `https://anthonywilliam0102.github.io/siglog-customer/` (GitHub Pages) → API `https://siglog-customer-api.onrender.com` (Render free, hiberna) → Supabase (login e-mail/GitHub, RLS). Variáveis do Pages: `VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_AUTH_PROVIDERS=github`. Modo demonstração do front (`VITE_DEMO=true`, `frontend/src/demo.js`) = API simulada no navegador, usado pelo Pages enquanto faltam as variáveis do sistema real. Tela Configurações (equipe): URL da API por navegador. Aba Integrações no menu da bolinha do usuário (todos veem o modo de cada squad; equipe configura URL/chave e testa a conexão; painéis WMS e Financeiro no detalhe do pedido, simulados sem URL, contratos são PROPOSTA). Integrações com squads (chave cifrada com Fernet em `integration_settings`, migração 0003, nunca devolvida; URL só https pública). Login com aba Criar conta (perfil cliente). Selo Student Help no rodapé. Integração entre squads: pasta `contracts/` (provided = gerado do código; consumed = um squad por pasta) e `docs/20_integracao_squads.md`; depois de mudar rotas/eventos rode `python scripts/gerar_contratos.py`. CI roda a suíte inteira. Entrega ao professor: fork + PR (`docs/19_entrega_professor.md`). JWT com tolerância de relógio de 30 s (`JWT_LEEWAY_SECONDS`).
Confirmado também (23/11): Jaeger com traces da API e Grafana com os painéis operacionais retornando dados.
**Pendente / NÃO VERIFICADO:** painéis de tickets, sinistros e satisfação com dados (falta gerar tráfego) · entrega dos eventos em uma fila (só há publicação) · executar o K6 e preencher `docs/13_load_test.md` ·
testes contra PostgreSQL/RabbitMQ reais · consumidores de eventos (Tracking, WMS, Financeiro — dependem dos contratos dos outros squads; formato do Tracking é SUPOSIÇÃO) ·
SonarCloud (`SONAR_TOKEN`) e Trivy bloqueante · UI/UX (CSD, Mapa de Empatia, Figma). **Release `v1.0.0` publicada em 28/11** (commit `5cf7ab0`, o mesmo do Render Live).

## Como o Claude deve trabalhar aqui
Entender antes de mudar, alterações pequenas e rastreáveis, rodar `ruff check .` e `pytest` antes de commitar, não inventar endpoints/arquivos,
classificar o que é CONFIRMADO / NÃO VERIFICADO, e registrar pendências em `docs/00_checklist.md`.
