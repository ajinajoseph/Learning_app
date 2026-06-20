import uuid

from app.extensions import db


class Question(db.Model):

    __tablename__ = "questions"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    quiz_id = db.Column(
        db.String(36),
        db.ForeignKey("quizzes.id"),
        nullable=False
    )

    question_text = db.Column(
        db.Text,
        nullable=False
    )

    def to_dict(self):

        return {
            "id": self.id,
            "quiz_id": self.quiz_id,
            "question_text": self.question_text
        }
    