# Segurança e DevSecOps

## Dados sensíveis
| Dado | Onde | Proteção |
|---|---|---|
| CPF/CNPJ, e-mail, telefone, endereço | `customers` | acesso somente pelo dono ou equipe (RN02); dados **fictícios** no projeto |
| Credenciais (DB, RabbitMQ, JWT) | `.env` local / GitHub Secrets | nunca versionadas (`.gitignore`) |
| Conteúdo de tickets/sinistros | `ticket_messages`, `claims` | mesmo controle de acesso |

## Autenticação e autorização
- **JWT** (`Authorization: Bearer`): **HS256** com `JWT_SECRET` ou **ES256/RS256** pelo JWKS do Supabase (`SUPABASE_URL`). `alg: none` e outros algoritmos são rejeitados. Claims obrigatórias: `sub`, `role` e **`exp`** (tokens sem expiração ou expirados são rejeitados).
- **Perfil** vem de `app_metadata.role` (nunca de `user_metadata`). `role: authenticated` do Supabase vira `cliente`; `anon` e `service_role` são rejeitados.
- **Perfis:** `cliente` (somente dados próprios), `atendente` e `gestor` (equipe: acesso a todos e alteração de status).
- Em desenvolvimento: `python scripts/gen_token.py <sub> <perfil> [horas]` (expira em 8 h por padrão).

## Proteção da API
Validação de entrada (Pydantic), respostas de erro sem detalhes internos, usuário não-root no container, imagem `slim`.

## Pipeline
Lint (ruff) → testes → build Docker → **Trivy** (imagem). **SonarCloud**: pendente (precisa do `SONAR_TOKEN`).

## Supabase
RLS habilitado em todas as tabelas (migração 0002) e sem policies: a Data API (`anon`) não acessa nada; só a nossa API, com o usuário `postgres`. Ver `docs/15_supabase.md`.

## Rede local
O Compose publica todas as portas apenas em `127.0.0.1`; outras máquinas da rede não alcançam banco, broker ou Grafana.

## Riscos conhecidos / melhorias
- `/metrics` e `/health` públicos → restringir por rede em produção.
- Rate limiting e CORS: definir quando o front existir.
- HS256 com segredo compartilhado; produção real preferiria RS256/JWKS.
