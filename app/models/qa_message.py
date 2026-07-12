import uuid

from app.extensions import db


class QAMessage(db.Model):

    __tablename__ = "qa_messages"

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

    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    channel = db.Column(
    db.String(20),
    nullable=False,
    default='forum'
    )

    parent_id = db.Column(
        db.String(36),
        db.ForeignKey("qa_messages.id"),
        nullable=True
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    is_deleted = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):
        from app.models.user import User
        user = User.query.get(self.user_id)
        user_name = user.name if user else "Student"
        return {
            "channel": self.channel,
            "id": self.id,
            "course_id": self.course_id,
            "user_id": self.user_id,
            "parent_id": self.parent_id,
            "message": self.message,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_name": user_name,
            "user": {"name": user_name}
        }
