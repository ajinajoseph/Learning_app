"""add payment provider ids

Revision ID: a1b2c3d4e5f6
Revises: 5ef6dc93de46
Create Date: 2026-06-24 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "5ef6dc93de46"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "payments",
        sa.Column("payment_intent_id", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "payments",
        sa.Column("order_id", sa.String(length=255), nullable=True),
    )


def downgrade():
    op.drop_column("payments", "order_id")
    op.drop_column("payments", "payment_intent_id")
