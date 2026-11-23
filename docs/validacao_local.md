# Validação local (executor no VS Code)

Arquivo do **Claude do VS Code**: adicionar sempre no fim, uma seção por rodada, com data, comandos e resultado
(CONFIRMADO / NÃO VERIFICADO / FALHOU). Não colar segredos. O checklist (`00_checklist.md`) é mantido pelo Claude da nuvem.

## 2026-11-23 — Rodada 1
- CONFIRMADO: build, migrate (0001), fluxo cliente → cotação → pedido, RN02 (403) e RN07 (422), Outbox publicado.
- FALHOU e corrigido (`1d2bc7d`): `httpx` fora do `requirements.txt`; API caía em loop na imagem.
- CONFIRMADO: Jaeger com traces da API; Grafana com login, datasource e dashboard; 9 de 12 painéis com dados.
- NÃO VERIFICADO: aparência do dashboard no navegador; painéis de tickets/sinistros/satisfação com dados.

## 2026-11-23 — Rodada 2 (Supabase)
Comando: `docker compose -f docker-compose.yml -f docker-compose.supabase.yml up -d --build`. Nenhum valor de `.env` foi impresso ou registrado.
- CONFIRMADO: `SUPABASE_URL/auth/v1/.well-known/jwks.json` responde 200 com 1 chave, `alg=ES256` (EC P-256, `use=sig`). Bate com a validação via JWKS descrita em `docs/15_supabase.md`.
- CONFIRMADO: stack sobe sem o Postgres local; `migrate` saiu com código 0 (o log do serviço vem vazio, a verificação foi feita no banco); API *healthy*; worker, RabbitMQ, Prometheus, Grafana e Jaeger no ar.
- CONFIRMADO: Alembic em `0002`; as 8 tabelas do domínio (claims, customers, feedback, orders, outbox_events, quotes, ticket_messages, tickets) com RLS ativo, mais `alembic_version` (9 no total, também com RLS). Nenhuma policy criada, como previsto.
- ACHADO: o projeto tem os usuários `cliente@exemplo.com` e `atendimento@exemplo.com`. Não existe `atendente@exemplo.com`, então o `update` do documento não afetaria nenhuma linha. Nenhum papel foi alterado; ambos seguem sem `role` em `app_metadata` (entram como cliente).
- NÃO VERIFICADO: promoção a atendente, login com token real do Supabase e `GET /customers/{id}` com cliente e atendente. Dependem do e-mail correto, das senhas e da chave `anon` (o `.env` não tem variável para ela).
- CONFIRMADO (mesma rodada, após autorização): `atendimento@exemplo.com` promovido com o SQL do documento (1 linha afetada); `app_metadata.role = atendente`. `cliente@exemplo.com` segue sem `role` (entra como cliente).
- NÃO VERIFICADO: login com token real e `GET /customers/{id}`; as senhas exportadas não estavam visíveis na sessão do Claude e falta a chave `anon`.

### Rodada 2 — login real e RN02 (Supabase)
Credenciais lidas de `.env.validacao` (ignorado pelo git); nenhum token, senha ou chave foi impresso ou registrado.
- CONFIRMADO: login em `/auth/v1/token?grant_type=password` → HTTP 200 para `cliente` e `atendimento`; os dois tokens vêm com `alg=ES256` e `aud=authenticated`. O token do atendente traz `app_metadata.role = atendente`; o do cliente não traz papel (entra como cliente).
- CONFIRMADO: `POST /customers` com o token do cliente → 201 (API validando token ES256 do Supabase via JWKS).
- CONFIRMADO: `GET /customers/{id}` com o cliente (dono) → 200; com o atendente → 200; sem token → 401.
- FALHOU / NÃO VERIFICADO: o 403 do segundo cliente. O `cliente2` do arquivo recebeu `invalid_credentials` no login e **não existe** em `auth.users` (só há `cliente@` e `atendimento@`). Sem token válido a chamada deu 401, o que não prova a RN02 em Supabase. Nenhum usuário foi criado.
- CONFIRMADO (parcial): RN02 contra o banco Supabase com um **token de desenvolvimento** (HS256, `sub` diferente, perfil cliente): `GET /customers/{id}` do cliente do Supabase → 403; dono → 200; atendente → 200. Isso prova a regra e que a API aceita HS256 junto com ES256, mas **não** é um segundo usuário real do Supabase (o projeto só tem `cliente@` e `atendimento@`).
- NÃO VERIFICADO: 403 com login real de um segundo cliente do Supabase (não existe usuário `cliente2`).

## 2026-11-23 — Rodada 3 (front + `GET /me`)
Nenhum token, senha ou chave foi impresso ou registrado.
- CONFIRMADO: `frontend/.env.local` criado a partir do `.env.example` (URL do Supabase e chave publishable; `VITE_API_URL` vazio) e **ignorado pelo git** (`.gitignore`, regra `.env.*`).
- CONFIRMADO: `TRACKING_MOCK=true` acrescentado ao `.env` (a linha não existia); o container da API recebe `TRUE`/`true`. Demais variáveis intactas.
- CONFIRMADO: stack com `docker-compose.supabase.yml` reconstruída; `migrate` saiu com 0, API *healthy*, worker no ar.
- CONFIRMADO: `npm install` e `npm run dev` (Vite 5.4, Node 24); `http://localhost:5173` responde 200 e o proxy `/api/health` responde 200.
- CONFIRMADO: `GET /me` com token real do Supabase: `cliente@exemplo.com` → 200, `role = cliente`; `atendimento@exemplo.com` → 200, `role = atendente`. Resultado igual direto na API (`:8000`) e pelo proxy do front (`:5173/api/me`).
- NÃO VERIFICADO: telas do front no navegador (login, cotação, pedidos, chamados, sinistros, atendimento); o teste foi só de HTTP.
