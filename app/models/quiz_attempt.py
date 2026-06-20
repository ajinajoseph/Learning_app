import uuid

from app.extensions import db


class QuizAttempt(db.Model):

    __tablename__ = "quiz_attempts"

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

    quiz_id = db.Column(
        db.String(36),
        db.ForeignKey("quizzes.id"),
        nullable=False
    )

    score = db.Column(
        db.Integer,
        default=0
    )

    submitted_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):

        return {
            "id": self.id,
            "student_id": self.student_id,
            "quiz_id": self.quiz_id,
            "score": self.score
        }