# Rodada de testes de segurança (28/11/2026)

## STATUS
Concluída contra uma **cópia local** (API em memória, testes automatizados em `tests/security/`). A produção **não** foi atacada.
138 testes passando (44 novos de segurança). Os 4 achados abaixo foram corrigidos e ficam cobertos por teste.

## ESCOPO
Autenticação (JWT), autorização (RN02, IDOR, escalada), validação de entrada, SSRF nas integrações, chaves da Nossa API, exposição de informação, cabeçalhos do front e dependências. **NÃO coberto:** teste de penetração na produção, Supabase/Render/Cloudflare em si, engenharia social, DoS distribuído.

## RESULTADO
| Área | Verificações | Resultado |
|---|---|---|
| JWT: sem token, `alg=none`, assinatura errada, expirado, sem `exp`/`sub`, `service_role`, `anon`, perfil inventado, `user_metadata` | 17 | **CONFIRMADO** negado ou sem elevação de perfil; HS256 desligado sem `JWT_SECRET` |
| RN02/IDOR: outro cliente lendo cliente, pedido, rastreamento, painéis, chamado, sinistro; filtro `customer_id`; escrever no chamado alheio | 12 | **CONFIRMADO** 403/404 |
| Escalada: cliente executando ações de equipe (status, configurações, chaves) | 5 | **CONFIRMADO** 403 |
| Injeção/XSS/path traversal em texto e parâmetros (SQL, `<script>`, `${}`, `../`, nulo, CRLF, 5000 caracteres, emoji) | 10 payloads × 2 rotas + parâmetros | **CONFIRMADO** sem erro de servidor; tabelas intactas; o front não usa `dangerouslySetInnerHTML` nem `innerHTML` |
| CPF/CNPJ inválidos, valores negativos/zero/enormes/não numéricos | 17 | **CONFIRMADO** 422 |
| SSRF nas integrações: IPs internos, `localhost`, metadados da nuvem, formatos numéricos, `file://`, usuário na URL, rebinding de DNS | 19 | **CONFIRMADO** recusado (exceto a porta, achado 3) |
| Nossa API: chave só lê pedidos; 11 rotas proibidas; variações da chave (maiúsculas, espaços, truncada) | 19 | **CONFIRMADO** 401/403/404/405/422, nenhuma aceitou |
| Erros sem stack trace, caminhos ou strings de banco | 2 | **CONFIRMADO** |
| CORS não reflete origem não autorizada | 1 | **CONFIRMADO** |
| Dependências Python (`pip-audit`) | todas | **CONFIRMADO** sem vulnerabilidade conhecida |

## ACHADOS E CORREÇÕES
1. **ALTO — Erro 500 com `Infinity`/`NaN` no JSON.** O FastAPI devolvia o valor enviado na resposta 422 e não conseguia serializá-lo, virando 500 (e ecoando a entrada do usuário). *Correção:* handler de `RequestValidationError` que devolve só `loc`, `msg` e `type` (`src/api/main.py`).
2. **MÉDIO — Textos sem limite de tamanho** (mensagem de chamado, descrição de sinistro, comentário): aceitou 200 KB. *Correção:* `max_length` (5000/5000/2000) e limite de corpo da requisição de 256 KB com 413 (`MAX_CORPO_BYTES`, `src/api/carga.py`).
3. **MÉDIO — SSRF: porta arbitrária** (`https://host-publico:22` era aceito). *Correção:* só portas 443 e 8443 (`src/infrastructure/clients/url_segura.py`).
4. **MÉDIO — `/metrics` público** na API publicada (expõe rotas e contagens). *Correção:* `METRICS_TOKEN` exige `Authorization: Bearer` quando definido; o `render.yaml` gera o valor no Render. Local/Prometheus do Compose seguem sem token.
5. **BAIXO — Front sem cabeçalhos de segurança.** *Correção:* `frontend/public/_headers` (CSP, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy`, `Permissions-Policy`), valido com o navegador sem violações. Vale para o Cloudflare Pages; o GitHub Pages não aplica `_headers`.

## RISCOS ACEITOS / PENDENTES
- **`react-router` (2 avisos moderados no `npm audit`):** redirecionamento aberto com barra invertida em `<Link>`/`navigate` e injeção na hidratação SSR. **Não explorável aqui:** todos os destinos de navegação são fixos ou internos e o front não usa SSR. A correção exige a versão 7 (mudança grande): **fazer depois do Demoday**.
- **Cadastro aberto no Supabase** (qualquer pessoa cria conta de perfil cliente): decisão para a demonstração. **Desligar depois do Demoday.**
- **Sem limite de requisições por usuário/IP** (só o limite global de requisições em andamento) e **sem bloqueio de tentativas de login** além do que o Supabase oferece. Risco aceito para o escopo acadêmico.
- **Documentação da API (`/docs`, `/openapi.json`) pública**, necessária para a integração com os outros squads.
- **Chaves de API da Nossa API** dão leitura de todos os pedidos: entregar por canal seguro e revogar após o uso.
- O limite de corpo se baseia no `Content-Length`; envio em partes (chunked) sem esse cabeçalho não é cortado aqui.
- Pendente: SonarCloud (análise estática) e teste de penetração real na produção, com autorização e janela definidas.

## COMO REPETIR
```bash
pytest tests/security -q
pip-audit -r requirements.txt
cd frontend && npm audit --omit=dev
```
