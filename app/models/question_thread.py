import uuid

from app.extensions import db


class QuestionThread(db.Model):

    __tablename__ = "question_threads"

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

    question = db.Column(
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
            "course_id": self.course_id,
            "student_id": self.student_id,
            "question": self.question,
            "created_at": self.created_at
        }