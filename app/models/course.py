import enum
import uuid

from app.extensions import db
from app.services.review_service import get_course_rating_stats

class CourseLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Course(db.Model):

    __tablename__ = "courses"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    title = db.Column(
        db.String(200),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    price = db.Column(
        db.Float,
        nullable=False,
        default=0,
    )

    level = db.Column(
        db.Enum(CourseLevel),
        nullable=False,
        default=CourseLevel.BEGINNER,
    )

    duration_hours = db.Column(
        db.Float,
        nullable=False,
        default=0,
    )

    language = db.Column(
        db.String(50),
        nullable=False,
        default="english",
    )

    tags = db.Column(
        db.JSON,
        nullable=True,
        default=list,
    )

    mentor_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False,
    )

    mentor = db.relationship(
        "User",
        backref="courses",
    )

    is_approved = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
    )

    def to_dict(self):
        rating = get_course_rating_stats(self.id)

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "level": self.level.value,
            "duration_hours": self.duration_hours,
            "language": self.language,
            "tags": self.tags or [],
            "mentor_id": self.mentor_id,
            "is_approved": self.is_approved,

            "average_rating": rating["average_rating"],
            "weighted_rating": rating["weighted_rating"],
            "total_reviews": rating["total_reviews"],
        }
