import uuid

from app.extensions import db


class Review(db.Model):

    __tablename__ = "reviews"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    course_id = db.Column(
        db.String(36),
        db.ForeignKey("courses.id"),
        nullable=False
    )

    student_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    comment = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    __table_args__ = (
        db.UniqueConstraint(
            "course_id",
            "student_id",
            name="one_review_per_student"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "student_id": self.student_id,
            "rating": self.rating,
            "comment": self.comment
        }