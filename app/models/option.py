import uuid

from app.extensions import db


class Option(db.Model):

    __tablename__ = "options"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    question_id = db.Column(
        db.String(36),
        db.ForeignKey("questions.id"),
        nullable=False
    )

    option_text = db.Column(
        db.String(255),
        nullable=False
    )

    is_correct = db.Column(
        db.Boolean,
        default=False
    )

    def to_dict(self):

        return {
            "id": self.id,
            "question_id": self.question_id,
            "option_text": self.option_text
        }