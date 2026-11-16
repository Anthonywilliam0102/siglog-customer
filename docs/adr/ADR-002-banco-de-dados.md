# ADR-002 — Banco de dados
**Status:** Aceita

**Contexto:** A.8 exige PostgreSQL isolado.
**Alternativas:** PostgreSQL local (container); Supabase (Postgres gerenciado); Cloudflare D1 (SQLite).
**Decisão:** PostgreSQL. Container local para dev/CI/testes; Supabase como banco hospedado opcional da demo.
**Justificativa:** D1 é SQLite e foge do enunciado. Supabase é gratuito e Postgres puro, sem lock-in (só `DATABASE_URL`).
**Consequências:** free tier do Supabase pausa por inatividade; migrações via Alembic mantêm os dois ambientes iguais; testes automáticos usam SQLite em memória (risco de divergência → validar também contra Postgres no CI numa fase futura).
