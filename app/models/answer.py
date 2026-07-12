import uuid

from app.extensions import db


class Answer(db.Model):

    __tablename__ = "answers"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    question_id = db.Column(
        db.String(36),
        db.ForeignKey(
            "question_threads.id"
        ),
        nullable=False
    )

    mentor_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    answer = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):

        return {
            "id": self.id,
            "question_id": self.question_id,
            "mentor_id": self.mentor_id,
            "answer": self.answer,
            "created_at": self.created_at
        }