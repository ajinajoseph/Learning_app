from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql  # add this

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():

    # Create enums via raw SQL — safe and idempotent
    op.execute("""
        CREATE TYPE reviewstatus AS ENUM ('PENDING', 'APPROVED', 'REJECTED')
    """)
    op.execute("""
        CREATE TYPE reportstatus AS ENUM ('PENDING', 'RESOLVED', 'DISMISSED')
    """)

    # QA MESSAGES
    op.create_table(
        "qa_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("course_id", sa.String(36), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("parent_id", sa.String(36), sa.ForeignKey("qa_messages.id")),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"))
    )

    # Use postgresql.ENUM — this NEVER auto-creates the type
    review_status_enum = postgresql.ENUM(
        "PENDING", "APPROVED", "REJECTED",
        name="reviewstatus",
        create_type=False
    )
    report_status_enum = postgresql.ENUM(
        "PENDING", "RESOLVED", "DISMISSED",
        name="reportstatus",
        create_type=False
    )

    op.add_column(
        "reviews",
        sa.Column("status", review_status_enum, nullable=False, server_default="APPROVED")
    )
    op.alter_column("reviews", "status", server_default=None)

    op.create_table(
        "review_reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("review_id", sa.String(36), sa.ForeignKey("reviews.id"), nullable=False),
        sa.Column("reporter_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", report_status_enum, nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.UniqueConstraint("review_id", "reporter_id", name="one_report_per_user")
    )


def downgrade():
    op.drop_table("review_reports")
    op.drop_column("reviews", "status")
    op.drop_table("qa_messages")
    op.execute("DROP TYPE IF EXISTS reportstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS reviewstatus CASCADE")