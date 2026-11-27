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
- `RUN_MIGRATIONS=true` (padrão do `render.yaml`): a API aplica o Alembic ao subir (idempotente); é assim que a tabela de integrações (migração 0003) chega ao Supabase.
- Opcional: na aba **Environment** do serviço, `SETTINGS_ENCRYPTION_KEY` (chave Fernet) permite à tela de Configurações guardar chaves de API dos outros squads. Sem ela, só a URL pode ser salva.
- Não há RabbitMQ nem worker na nuvem: os eventos ficam no Outbox (tabela `outbox_events`). O fluxo do portal funciona normalmente; a publicação no RabbitMQ é mostrada na demo local.

### 2A. Front no GitHub Pages (recomendado: sem conta nova, publica sozinho a cada push na `main`)
**Atalho para ter uma URL em minutos:** só habilite o Pages (passo 1 abaixo). Sem as variáveis, o workflow publica o **modo demonstração**: o portal completo com dados fictícios simulados no navegador, com uma faixa de aviso "Modo demonstração" em todas as telas. Não é o sistema real, mas serve para mostrar o visual e os fluxos; quando criar as variáveis (passo 2) e rodar de novo, ele passa a usar a API e o Supabase de verdade.
1. No repositório: **Settings → Pages → Build and deployment → Source: GitHub Actions** (uma vez só).
2. **Settings → Secrets and variables → Actions → aba Variables → New repository variable**, três variáveis:
   `VITE_API_URL` (URL da API do passo 1, sem barra no fim), `VITE_SUPABASE_URL` e `VITE_SUPABASE_PUBLISHABLE_KEY` (chave **publishable**; nunca a secret).
3. **Actions → "Publicar portal (GitHub Pages)" → Run workflow** (ou faça um push em `frontend/`). O endereço será `https://<usuario>.github.io/<repositorio>/` (aparece no fim do job).
4. Se alguma das três variáveis faltar, o workflow publica o modo demonstração (e avisa no log); só com as três ele publica o sistema real.

### 2B. Front no Cloudflare Pages (alternativa)
1. Cloudflare → **Workers & Pages → Create → Pages → Connect to Git** → repositório → branch `main`.
2. Configuração: **Root directory** `frontend` · **Build command** `npm run build` · **Build output** `dist`.
3. Variáveis de ambiente (build): `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY` (chave **publishable**, nunca a secret), `VITE_API_URL` = URL da API do passo 1 (sem barra no fim), `NODE_VERSION` = `22`.
4. Anote a URL `https://<projeto>.pages.dev`. O `frontend/public/_redirects` já cuida das rotas do React.

### 3. Ligar os dois
- No Render, defina `CORS_ORIGINS` = **só a origem** do front, sem caminho e sem barra (GitHub Pages: `https://<usuario>.github.io`; Cloudflare: `https://<projeto>.pages.dev`) e salve (a API reinicia).
- No Supabase, **Authentication → URL Configuration → Site URL** = a URL completa do front.
- Teste: abra a URL do Pages, entre com o cliente e faça uma cotação.

## URL do sistema REAL agora, a partir do seu computador (Cloudflare Tunnel)
Expõe o sistema que está rodando na sua máquina (banco no Supabase) numa URL pública temporária, sem conta no Cloudflare:
```bash
winget install Cloudflare.cloudflared            # uma vez (PowerShell/Git Bash)
docker compose -f docker-compose.yml -f docker-compose.supabase.yml up -d --build
cd frontend && npm run dev                       # em outro terminal; http://localhost:5173
cloudflared tunnel --url http://localhost:5173   # imprime https://<nome>.trycloudflare.com
```
Uma única URL serve o portal e a API (o Vite faz o proxy de `/api`). A URL muda a cada execução, vale só enquanto o computador e o comando estiverem ligados, e **qualquer pessoa com o link consegue abrir a tela de login**: use para demonstrar e feche depois (Ctrl+C).
Para algo permanente com domínio seu no Cloudflare existe o *named tunnel* (exige conta e um domínio na conta). O Cloudflare **não hospeda** a API Python: a API precisa do Render (ou de um túnel como este).

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
| `pages.yml` (GitHub Pages) e o front sob subcaminho `/<repositorio>/` | build e roteamento testados localmente; **o deploy em si NÃO VERIFICADO** (precisa habilitar o Pages e criar as variáveis) |
| API no Render, CORS e URL do Supabase | **NÃO VERIFICADO** (dependem da conta do time) |
| Limites do plano gratuito do Render e do Pages | **NÃO VERIFICADO** (podem ter mudado; confira nos painéis) |
