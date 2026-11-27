"""habilita RLS nas tabelas (Supabase expõe o schema public pela Data API)

Sem policies = anon/authenticated não leem nem escrevem nada. A API acessa com o usuário dono
das tabelas (postgres), que ignora RLS. Em bancos que não são PostgreSQL não faz nada.

Revision ID: 0002
Revises: 0001
"""
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

TABLES = ["customers", "quotes", "orders", "tickets", "ticket_messages", "claims", "feedback",
          "outbox_events", "alembic_version"]


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    for t in TABLES:
        op.execute(f"ALTER TABLE {t} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    for t in TABLES:
        op.execute(f"ALTER TABLE {t} DISABLE ROW LEVEL SECURITY")
