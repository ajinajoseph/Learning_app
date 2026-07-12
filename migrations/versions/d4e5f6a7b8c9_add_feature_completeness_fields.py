"""add feature completeness fields

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_approved",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            )
        )

    with op.batch_alter_table("modules", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "sort_order",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )

    with op.batch_alter_table("lessons", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "sort_order",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )

    with op.batch_alter_table("quizzes", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "pass_percentage",
                sa.Float(),
                nullable=False,
                server_default="70",
            )
        )

    op.create_table(
        "lesson_attachments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("lesson_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("file_key", sa.String(length=500), nullable=False),
        sa.Column("file_type", sa.String(length=50), nullable=True),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("lesson_attachments")

    with op.batch_alter_table("quizzes", schema=None) as batch_op:
        batch_op.drop_column("pass_percentage")

    with op.batch_alter_table("lessons", schema=None) as batch_op:
        batch_op.drop_column("sort_order")

    with op.batch_alter_table("modules", schema=None) as batch_op:
        batch_op.drop_column("sort_order")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("is_approved")
