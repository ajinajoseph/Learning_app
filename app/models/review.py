import enum
import uuid

from app.extensions import db


class ReviewStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Review(db.Model):

    __tablename__ = "reviews"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    course_id = db.Column(
        db.String(36),
        db.ForeignKey("courses.id"),
        nullable=False,
    )

    student_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False,
    )

    rating = db.Column(
        db.Integer,
        nullable=False,
    )

    comment = db.Column(
        db.Text,
        nullable=True,
    )

    status = db.Column(
    db.Enum(
        ReviewStatus,
        name="reviewstatus",
        create_type=False
    ),
    nullable=False,
    default=ReviewStatus.PENDING,
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "course_id",
            "student_id",
            name="one_review_per_student",
        ),
    )

    def to_dict(self):
        from app.models.user import User
        student = User.query.get(self.student_id)
        return {
            "id": str(self.id),
            "course_id": str(self.course_id),
            "student_id": str(self.student_id),
            "rating": self.rating,
            "comment": self.comment,
            "status": self.status.value if hasattr(self.status, 'value') else self.status,
            "student_name": student.name if student else "Student",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
