# Publicação: sistema no ar para o Demoday

Arquitetura publicada: **front** (Cloudflare Pages) → **API** (Render, Docker) → **banco** (Supabase). Login pelo Supabase Auth.
Segredos só nos painéis (nunca no repositório). Todos os passos abaixo são feitos **pelo time**; o status de cada um está na última seção.

## Ordem (o front precisa da URL da API na hora do build)
### 1. API no Render
1. render.com → **New → Blueprint** → conecte o repositório e escolha o `render.yaml` (plano *Free*, runtime Docker).
2. Preencha as variáveis marcadas como segredo no painel:
   - `DATABASE_URL` → string do **Session pooler** do Supabase, com prefixo `postgresql+psycopg://` e `?sslmode=require` (ver `docs/15_supabase.md`).
   - `SUPABASE_URL` → `https://<ref>.supabase.co`.
   - `CORS_ORIGINS` → deixe para o passo 3 (URL do Pages) e volte aqui depois.
3. **Não** crie `JWT_SECRET` na nuvem: sem ele, tokens de desenvolvimento (HS256) são recusados e só valem os do Supabase.
4. Quando subir, abra `https://<api>.onrender.com/health`: deve responder `{"status":"ok",...}`. Anote essa URL.
- O plano gratuito **hiberna após inatividade**: a primeira chamada pode levar cerca de 1 minuto. **Abra o `/health` alguns minutos antes de apresentar.**
- O banco já está migrado (Alembic 0002). Se criar um banco novo, defina `RUN_MIGRATIONS=true` uma vez.
- Não há RabbitMQ nem worker na nuvem: os eventos ficam no Outbox (tabela `outbox_events`). O fluxo do portal funciona normalmente; a publicação no RabbitMQ é mostrada na demo local.

### 2. Front no Cloudflare Pages
1. Cloudflare → **Workers & Pages → Create → Pages → Connect to Git** → repositório → branch `main`.
2. Configuração: **Root directory** `frontend` · **Build command** `npm run build` · **Build output** `dist`.
3. Variáveis de ambiente (build): `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY` (chave **publishable**, nunca a secret), `VITE_API_URL` = URL da API do passo 1 (sem barra no fim), `NODE_VERSION` = `22`.
4. Anote a URL `https://<projeto>.pages.dev`. O `frontend/public/_redirects` já cuida das rotas do React.

### 3. Ligar os dois
- No Render, defina `CORS_ORIGINS` = a URL do Pages (exata, sem barra) e salve (a API reinicia).
- No Supabase, **Authentication → URL Configuration → Site URL** = a URL do Pages.
- Teste: abra a URL do Pages, entre com o cliente e faça uma cotação.

## Plano B (se a hospedagem falhar ou o plano gratuito mudar): local + túnel
Roda tudo no notebook de quem apresenta e expõe **uma** URL pública:
```bash
docker compose -f docker-compose.yml -f docker-compose.supabase.yml up -d --build
cd frontend && npm run dev                      # http://localhost:5173 (já faz proxy de /api para a API)
cloudflared tunnel --url http://localhost:5173  # imprime https://<nome>.trycloudflare.com
```
Instalar o `cloudflared`: `winget install Cloudflare.cloudflared`. A URL muda a cada execução e só vale enquanto o notebook estiver ligado.

## Checklist do dia da demo
- [ ] `https://<api>/health` respondendo (acordar a API com antecedência)
- [ ] Login com `cliente@exemplo.com` e `atendimento@exemplo.com` na URL pública
- [ ] Um pedido de teste já criado (plano B se algo travar)
- [ ] Ambiente local de pé (Docker, Grafana, RabbitMQ, Jaeger) para mostrar eventos e observabilidade
- [ ] Deck aberto, com os resultados do K6 preenchidos

## Status
| Item | Situação |
|---|---|
| `render.yaml`, `Dockerfile` (PORT), `start.sh`, `_redirects` | CONFIRMADO no código; a imagem sobe na porta de `PORT` (smoke test no CI) |
| API no Render, front no Pages, CORS e URL do Supabase | **NÃO VERIFICADO** (dependem das contas do time) |
| Limites do plano gratuito do Render e do Pages | **NÃO VERIFICADO** (podem ter mudado; confira nos painéis) |
