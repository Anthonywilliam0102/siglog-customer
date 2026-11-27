# Banco de Dados

**SGBD:** PostgreSQL (Database-per-Service). Dev/CI: container `postgres:16`. Demo (opcional): Supabase. Migrações: **Alembic** (`migrations/`), `alembic upgrade head` roda no serviço `migrate` do Compose.

## Tabelas
| Tabela | Descrição | Observações |
|---|---|---|
| customers | clientes PF/PJ | `documento` único (somente dígitos); `owner_sub` = usuário dono (RN02) |
| quotes | cotações | `expires_at` (24h), `accepted` |
| orders | pedidos | `quote_id` único (1 pedido por cotação); `status` |
| tickets / ticket_messages | SAC e atendimentos | `sla_due_at` por prioridade |
| claims | sinistros | vinculados a pedido e cliente |
| feedback | avaliações | únicas por (pedido, alvo) e (ticket, alvo) |
| outbox_events | eventos pendentes de publicação | `published_at` nulo = pendente |

```
customers 1─* quotes 1─1 orders 1─* claims
customers 1─* tickets 1─* ticket_messages
orders 1─* tickets (opcional)    orders/tickets 1─1 feedback (por alvo)
```
Status guardados como texto validado pelo domínio (evita enums nativos e migrações complexas).

## Supabase (se usado na demo)
- Usar a **connection string do pooler** em `DATABASE_URL` (via `.env`/GitHub Secrets, nunca no repositório).
- Rodar `alembic upgrade head` apontando para o Supabase.
- Se o projeto for pausado por inatividade, reativar no painel antes da demo.
- Ativar RLS nas tabelas caso o front acesse o banco direto; no desenho atual o front acessa **somente a API**.
