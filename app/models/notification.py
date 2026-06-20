import uuid

from app.extensions import db


class Notification(db.Model):

    __tablename__ = "notifications"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):

        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at
        }