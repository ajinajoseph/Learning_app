import uuid

from app.extensions import db


class Quiz(db.Model):

    __tablename__ = "quizzes"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    lesson_id = db.Column(
        db.String(36),
        db.ForeignKey("lessons.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):

        return {
            "id": self.id,
            "title": self.title,
            "lesson_id": self.lesson_id
        }