"""add course search fields

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None

course_level = sa.Enum(
    "BEGINNER",
    "INTERMEDIATE",
    "ADVANCED",
    name="courselevel",
)


def upgrade():
    course_level.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "courses",
        sa.Column(
            "level",
            course_level,
            nullable=False,
            server_default="BEGINNER",
        ),
    )
    op.add_column(
        "courses",
        sa.Column(
            "duration_hours",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "courses",
        sa.Column(
            "language",
            sa.String(length=50),
            nullable=False,
            server_default="english",
        ),
    )
    op.add_column(
        "courses",
        sa.Column("tags", sa.JSON(), nullable=True),
    )

    op.alter_column("courses", "level", server_default=None)
    op.alter_column("courses", "duration_hours", server_default=None)
    op.alter_column("courses", "language", server_default=None)


def downgrade():
    op.drop_column("courses", "tags")
    op.drop_column("courses", "language")
    op.drop_column("courses", "duration_hours")
    op.drop_column("courses", "level")
    course_level.drop(op.get_bind(), checkfirst=True)
