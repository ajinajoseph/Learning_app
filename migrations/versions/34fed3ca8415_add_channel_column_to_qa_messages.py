"""add channel column to qa_messages"""

from alembic import op
import sqlalchemy as sa

revision = "34fed3ca8415"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("qa_messages") as batch_op:
        batch_op.add_column(
            sa.Column(
                "channel",
                sa.String(length=20),
                nullable=False,
                server_default="forum",
            )
        )

    # Remove the default afterwards if you don't want PostgreSQL
    # automatically filling future rows.
    with op.batch_alter_table("qa_messages") as batch_op:
        batch_op.alter_column("channel", server_default=None)


def downgrade():
    with op.batch_alter_table("qa_messages") as batch_op:
        batch_op.drop_column("channel")