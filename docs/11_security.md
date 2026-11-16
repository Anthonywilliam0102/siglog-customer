# Segurança e DevSecOps

## Dados sensíveis
| Dado | Onde | Proteção |
|---|---|---|
| CPF/CNPJ, e-mail, telefone, endereço | `customers` | acesso somente pelo dono ou equipe (RN02); dados **fictícios** no projeto |
| Credenciais (DB, RabbitMQ, JWT) | `.env` local / GitHub Secrets | nunca versionadas (`.gitignore`) |
| Conteúdo de tickets/sinistros | `ticket_messages`, `claims` | mesmo controle de acesso |

## Autenticação e autorização
- **JWT HS256** (`Authorization: Bearer`), validado com `JWT_SECRET`; compatível com o JWT secret do Supabase Auth. Claims: `sub`, `role`.
- **Perfis:** `cliente` (somente dados próprios), `atendente` e `gestor` (equipe: acesso a todos e alteração de status).
- Em desenvolvimento: `python scripts/gen_token.py <sub> <perfil>`.

## Proteção da API
Validação de entrada (Pydantic), respostas de erro sem detalhes internos, usuário não-root no container, imagem `slim`.

## Pipeline
Lint (ruff) → testes → build Docker → **Trivy** (imagem). **SonarCloud**: pendente (precisa do `SONAR_TOKEN`).

## Riscos conhecidos / melhorias
- `/metrics` e `/health` públicos → restringir por rede em produção.
- Rate limiting e CORS: definir quando o front existir.
- HS256 com segredo compartilhado; produção real preferiria RS256/JWKS.
