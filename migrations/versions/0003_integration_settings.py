"""configuração de integrações com outros squads (URL base e chave de API cifrada)

Revision ID: 0003
Revises: 0002
"""
import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "integration_settings",
        sa.Column("squad", sa.String(length=20), nullable=False),
        sa.Column("base_url", sa.String(length=300), nullable=True),
        sa.Column("header_name", sa.String(length=64), nullable=False),
        sa.Column("api_key_enc", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint("squad"),
    )
    if op.get_bind().dialect.name == "postgresql":  # mesma política da 0002: RLS sem policies
        op.execute("ALTER TABLE integration_settings ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.drop_table("integration_settings")
