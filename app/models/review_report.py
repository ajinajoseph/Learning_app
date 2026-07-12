import enum
import uuid

from app.extensions import db


class ReportStatus(enum.Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ReviewReport(db.Model):

    __tablename__ = "review_reports"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    review_id = db.Column(
        db.String(36),
        db.ForeignKey("reviews.id"),
        nullable=False,
    )

    reporter_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False,
    )

    reason = db.Column(
        db.Text,
        nullable=False,
    )

    status = db.Column(
    db.Enum(
        ReportStatus,
        name="reportstatus",
        create_type=False
    ),
    nullable=False,
    default=ReportStatus.PENDING,
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "review_id",
            "reporter_id",
            name="one_report_per_user",
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "review_id": self.review_id,
            "reporter_id": self.reporter_id,
            "reason": self.reason,
            "status": self.status.value,
            "created_at": self.created_at,
        }
