"""chaves de API emitidas para outros squads consultarem o CRM (só o hash é guardado)

Revision ID: 0004
Revises: 0003
"""
import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("squad", sa.String(length=20), nullable=False),
        sa.Column("nome", sa.String(length=80), nullable=False),
        sa.Column("prefixo", sa.String(length=12), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
    )
    if op.get_bind().dialect.name == "postgresql":  # mesma política da 0002: RLS sem policies
        op.execute("ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.drop_table("api_keys")
