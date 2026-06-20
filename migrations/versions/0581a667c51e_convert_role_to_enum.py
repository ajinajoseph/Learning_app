"""Convert role to enum

Revision ID: 0581a667c51e
Revises: 7a6b4694b662
"""

from alembic import op
import sqlalchemy as sa


revision = "0581a667c51e"
down_revision = "7a6b4694b662"
branch_labels = None
depends_on = None


user_role_enum = sa.Enum(
    "ADMIN",
    "MENTOR",
    "STUDENT",
    name="userrole"
)


def upgrade():


    user_role_enum.create(
        op.get_bind(),
        checkfirst=True
    )

    # Convert column
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role
        TYPE userrole
        USING upper(role)::userrole
    """)


def downgrade():

    op.execute("""
        ALTER TABLE users
        ALTER COLUMN role
        TYPE VARCHAR(20)
    """)

    user_role_enum.drop(
        op.get_bind(),
        checkfirst=True
    )