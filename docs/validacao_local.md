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
- CONFIRMADO: `TRACKING_MOCK=true` acrescentado ao `.env` (a linha não existia); o container da API recebe `true`. Demais variáveis intactas.
- CONFIRMADO: stack com `docker-compose.supabase.yml` reconstruída; `migrate` saiu com 0, API *healthy*, worker no ar.
- CONFIRMADO: `npm install` e `npm run dev` (Vite 5.4, Node 24); `http://localhost:5173` responde 200 e o proxy `/api/health` responde 200.
- CONFIRMADO: `GET /me` com token real do Supabase: `cliente@exemplo.com` → 200, `role = cliente`; `atendimento@exemplo.com` → 200, `role = atendente`. Resultado igual direto na API (`:8000`) e pelo proxy do front (`:5173/api/me`).
- NÃO VERIFICADO: telas do front no navegador (login, cotação, pedidos, chamados, sinistros, atendimento); o teste foi só de HTTP.

### Rodada 3 — telas do front no navegador
Chrome headless (puppeteer-core, instalado fora do repositório), login real pela tela em `http://localhost:5173`, API com Supabase. Sem tokens, senhas ou chaves no registro.
- CONFIRMADO: login pela tela com `cliente@exemplo.com` e `atendimento@exemplo.com` leva a `/` ("Olá, Cliente" / "Painel da equipe").
- CONFIRMADO (cliente): `/`, `/cotacao`, `/pedidos`, `/chamados`, `/chamados/novo`, `/sinistros`, `/sinistros/novo` carregam com o título esperado, sem erro de console e sem resposta HTTP 4xx/5xx.
- CONFIRMADO (atendente): `/`, `/pedidos`, `/chamados`, `/sinistros`, `/atendimento` ("Fila de atendimento") carregam sem erros. O menu muda por perfil: só a equipe vê "Atendimento".
- CONFIRMADO (RN02 na UI): o cliente que abre `/atendimento` é redirecionado para `/`.
- OBSERVAÇÃO: `/cadastro` redireciona o cliente para `/` (ele já tem cadastro, criado na rodada anterior).
- NÃO VERIFICADO: `/pedidos/:id`, porque o banco Supabase ainda não tem pedidos (listas vazias); ações que gravam (calcular cotação, confirmar pedido, abrir chamado/sinistro, mudar status); chamado e sinistro com dados.
- FALHOU (intermitente, causa NÃO provada): em 3 execuções seguidas, logo após o login do cliente o `GET /api/me` voltou **401** e o front deslogou (voltou a `/login` sem mensagem). Depois disso o mesmo fluxo passou em todas as tentativas (30 chamadas seguidas com um token e 8 logins com chamada imediata, todas 200). Também houve um 401 isolado por curl no atendente. Descartado: relógio (host, container e `iat` coerentes) e instabilidade do JWKS (30 de 30 respostas 200, máx. 0,45 s). Hipótese aberta: renovação do cache do JWKS (300 s) no PyJWT. Para o Claude da nuvem investigar; a API só loga "401 Unauthorized" e não registra a exceção.

### Rodada 3 — ações que gravam, pela interface (Chrome headless, login real, API com Supabase)
Dados 100% fictícios, criados nas contas `cliente@` e `atendimento@`. Sem tokens, senhas ou chaves no registro.
- CONFIRMADO (18/18 passos): cliente calcula cotação (R$ 210,00 para 80 kg e 0,8 m³) → confirma pedido → abre chamado a partir do pedido → registra sinistro (tipo AVARIA); atendente abre o pedido do cliente (RN02: equipe vê tudo), avança **CRIADO → EM_SEPARACAO → EM_TRANSPORTE → ENTREGUE** pelos botões, não vê mais transições possíveis num pedido ENTREGUE (RN07), vê o chamado na fila de atendimento, responde e marca como resolvido; cliente avalia o atendimento (5) e a entrega (4), vê o rastreamento rotulado "simulado" (`TRACKING_MOCK`) e é barrado em `/atendimento`.
- CONFIRMADO no banco Supabase: pedido `ENTREGUE`; chamado `RESOLVIDO` com 3 mensagens e prazo de SLA preenchido; sinistros `REGISTRADO`; avaliações `ENTREGA`=4 e `ATENDIMENTO`=5; Outbox com 12 eventos, **todos publicados** (cotacao.solicitada, pedido.criado, chamado.aberto, sinistro.registrado, cliente.notificado x3, entrega.avaliada). O catálogo `docs/08_events.md` não prevê evento de avaliação de atendimento, então a ausência é coerente.
- Sobras de teste: uma primeira execução parcial deixou 1 pedido em `CRIADO`, 1 chamado `ABERTO` e 1 sinistro; as listas do Supabase têm 2 pedidos, 2 chamados e 2 sinistros.
- FALHOU (intermitente, **reproduzido**): o login do **atendente** precisou de **2 tentativas** na execução final; na primeira, o `GET /api/me` voltou 401 e o front voltou para `/login` sem mensagem (a API registrou o 401). Nas execuções anteriores o mesmo ocorreu 3 vezes com o cliente. Um novo login logo em seguida funciona. Impacto: o usuário vê a tela de login "sem motivo" e precisa tentar de novo. Causa NÃO provada.
- Hipóteses: (a) relógio — descartado em medições pontuais (host, container e `iat` coerentes, 8 de 8 logins com 200), mas o relógio do container **saltou ~1 h** durante um `sleep` de 310 s, o que indica que a VM do Docker Desktop é suspensa e ressincronizada; defasagem logo após esse ressincronismo poderia gerar `iat` "no futuro" e 401. Não testado de forma controlada. (b) expiração do cache do JWKS (300 s): o experimento planejado ficou **inválido** (o token expirou por causa do salto de relógio) e não prova nada. Descartado: indisponibilidade do JWKS (30 de 30 respostas 200, máx. 0,45 s).
- Sugestão para o Claude da nuvem: logar a exceção do `_decode` (classe e mensagem, sem o token) para identificar a causa; considerar tolerância pequena de relógio (`leeway`) na validação do JWT; o front poderia repetir o `/me` uma vez antes de deslogar.

## 2026-11-26 — Rodada 4 (E2E em modo Supabase e reteste do 401) — código `8b299db`
Credenciais lidas de `.env.validacao`; nenhum token, senha ou chave foi impresso ou registrado.
- **FALHOU (bloqueia a subida no Windows):** `docker compose -f docker-compose.yml -f docker-compose.supabase.yml up -d --build` deixa a API em loop (`exit 2`): `/app/start.sh: 3: set: Illegal option -`. Causa: `scripts/start.sh` está em LF no repositório (`i/lf`), mas com `core.autocrlf=true` o checkout no Windows grava CRLF (`w/crlf`) e o Dockerfile copia o arquivo assim. Em Linux/CI não aparece, por isso o smoke test da imagem não pega. **Correção sugerida (Claude da nuvem):** `.gitattributes` com `*.sh text eol=lf` (e/ou `sed -i 's/\r$//'` no Dockerfile).
- Contorno usado só nesta validação (nenhum arquivo do projeto alterado): override temporário fora do repositório com `command: ["sh","-c","tr -d '\r' < /app/start.sh | sh"]`. **Os resultados abaixo foram obtidos com esse contorno**; sem ele a API não sobe nesta máquina.
- CONFIRMADO: `migrate` saiu com 0; API *healthy*; `jwt_leeway_seconds = 30` no container; front (Vite) e proxy `/api/health` respondendo.
- CONFIRMADO: E2E (`E2E_MODE=supabase E2E_CHANNEL=chrome`) → **16/16 verificações OK**, exit 0.
- CONFIRMADO: 10 logins novos do cliente, cada um seguido imediatamente de 20 chamadas a `/me` (alternando API direta e proxy do front) → **200/200 com HTTP 200**, inclusive as 10 primeiras chamadas. Nenhum `auth_failed` no log da API desde o início do container (inclui o período do E2E).
- OBSERVAÇÃO sobre a causa do 401: nesses logins `iat - relógio do host` variou de 0 a **+1 s**, ou seja, o token pode chegar "do futuro". Isso é compatível com a explicação do relógio que o `leeway` corrige. Não está provado: o 401 antigo não foi reproduzido com a exceção registrada. Se voltar, o log `auth_failed` traz o motivo.
- ATENÇÃO (README do E2E): o padrão `E2E_BASE_URL=http://127.0.0.1:5173` não responde nesta máquina (o Vite escuta só em `localhost`). Foi usado `E2E_BASE_URL=http://localhost:5173`.
- `npm install` em `tests/e2e` gera `package-lock.json` não versionado; decidir se entra no repositório (não commitado aqui).
- O E2E criou dados fictícios no Supabase (pedido, chamado, sinistro, avaliações).

## 2026-11-26 — Rodada 5 (sem contorno de CRLF, E2E, entrega de eventos, seed e K6) — código `ab968db`
Nenhum token, senha ou chave foi impresso ou registrado. Máquina: i5-12450H (12 threads), 11,7 GB de RAM; Docker com 12 CPUs e ~5,6 GB.

### 1. Build com Supabase, sem override
- CONFIRMADO: API *healthy*, 0 reinícios, `migrate` saiu com 0. A cópia de trabalho ainda tinha `start.sh` em CRLF; o `sed` do Dockerfile resolveu (sem `\r` dentro da imagem).

### 2. Front e E2E (`E2E_MODE=supabase E2E_CHANNEL=chrome`)
- FALHOU: **15/16 em duas execuções seguidas**; só "rastreamento com 4 eventos".
- Diagnóstico: o portal está certo. Num pedido novo, a tela tinha 0 itens em `.eventos li` no instante em que o teste conta (700 ms após o último clique) e 4 itens 0,5 s depois, também após recarregar; a API devolve 4 eventos. **É corrida no teste** (`tests/e2e/portal.e2e.cjs`): trocar a contagem imediata por uma espera (ex.: aguardar o 4º `.eventos li`).
- Continua necessário `E2E_BASE_URL=http://localhost:5173` (o padrão `127.0.0.1` não responde nesta máquina).

### 3. Entrega dos eventos em fila
- CONFIRMADO: `consumir_eventos.py --fila teste-vscode --chave "customer.#" --max 3 --timeout 90` recebeu **CotacaoSolicitada** e **PedidoCriado** de um pedido criado pela API durante a espera. Total 2 (o 3º não veio e o consumidor encerrou por tempo; exit 0).
- A fila `teste-vscode` foi apagada depois (0 mensagens), para não acumular os eventos do seed e da carga.

### 4. Seed de demonstração (uma única execução, Supabase)
- CONFIRMADO: `seed_demo.py --sim` OK. Acrescentou 5 pedidos, 3 chamados, 2 sinistros e 3 avaliações; Outbox sem pendentes. Totais após o seed: 1 cliente, 12 pedidos, 8 chamados, 7 sinistros, 11 avaliações (inclui sobras dos testes anteriores). **Não rodar de novo** (duplica).

### 5. K6 (60 s por cenário) — FALHOU
Rodado contra o **Postgres local**, não o Supabase. ATENÇÃO: o passo `docker compose up -d --build` de `docs/13_load_test.md` usa a `DATABASE_URL` do `.env`; com o `.env` apontando para o Supabase, a carga iria para o banco do Demoday. Foi usado override temporário (fora do repositório) fixando `DATABASE_URL` no Postgres local, e conferido o host antes. Outro desvio: K6 na rede do Compose (`BASE_URL=http://api:8000`) em vez de `--network host`.

| Cenário | Média | p95 | p99 | Throughput obtido | Erros | Iterações descartadas |
|---|---|---|---|---|---|---|
| Normal (alvo 100 req/s) | 20,85 s | 60 s (timeout) | 60 s (timeout) | 5,3 req/s (475 req) | 33,89% | 5448 |
| Pico (alvo 500 req/s) | 53,45 s | 60 s (timeout) | 60 s (timeout) | 12,2 req/s (1101 req) | 89,00% | 28857 |
| Extremo | NÃO EXECUTADO: a API já não resistiu ao pico | | | | | |

Só respostas bem-sucedidas: normal média 4,69 s / p95 31,22 s / p99 31,33 s; pico média 6,9 s / p95 31,82 s / p99 32,46 s. Nenhum threshold passou.

**Defeito encontrado (crítico para o Demoday):**
- Log da API: `sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached ... timeout 30.00` (398 ocorrências somando os dois cenários).
- Depois do cenário normal a API voltou sozinha. **Depois do pico ficou travada**: `/health` sem resposta por mais de 6 minutos, CPU da API ~0,3%, e **15 conexões `idle in transaction`** há mais de 3 minutos (= pool inteiro 5+10). Só voltou com a recriação do container; o Compose não reinicia container *unhealthy*.
- Causa provável (NÃO provada): rotas `def` síncronas + `get_session` com `yield` em `src/infrastructure/db.py`. As threads do threadpool (40) ficam esperando conexão enquanto o fechamento das sessões que as liberariam também depende de thread: bloqueio mútuo.
- Vale para qualquer ambiente com este código, inclusive o publicado: uma rajada pode derrubar a API até alguém reiniciar.
- Para o Claude da nuvem avaliar: liberar a conexão antes de responder (também nas leituras), dimensionar pool e threadpool juntos, `pool_timeout` curto; depois repetir o K6. `docs/13_load_test.md` não foi alterado.

### Estado ao final
Stack de volta ao Supabase, API *healthy*, contagens do Supabase iguais às de depois do seed (a carga não o tocou). Postgres local parado. Vite rodando em `localhost:5173`.
