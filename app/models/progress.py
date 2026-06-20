import uuid

from app.extensions import db


class Progress(db.Model):

    __tablename__ = "progress"

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

    lesson_id = db.Column(
        db.String(36),
        db.ForeignKey("lessons.id"),
        nullable=False
    )

    completed = db.Column(
        db.Boolean,
        default=False
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "lesson_id",
            name="unique_lesson_progress"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "lesson_id": self.lesson_id,
            "completed": self.completed
        }