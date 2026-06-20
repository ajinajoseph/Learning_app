import uuid

from app.extensions import db


class Enrollment(db.Model):

    __tablename__ = "enrollments"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    student_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    course_id = db.Column(
        db.String(36),
        db.ForeignKey("courses.id"),
        nullable=False
    )

    enrolled_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "course_id",
            name="unique_enrollment"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "enrolled_at": self.enrolled_at
        }