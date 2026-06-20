import uuid

from app.extensions import db


class Lesson(db.Model):

    __tablename__ = "lessons"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=True
    )

    video_url = db.Column(
        db.String(500),
        nullable=True
    )

    pdf_url = db.Column(
        db.String(500),
        nullable=True
    )

    module_id = db.Column(
        db.String(36),
        db.ForeignKey("modules.id"),
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
            "content": self.content,
            "video_url": self.video_url,
            "pdf_url": self.pdf_url,
            "module_id": self.module_id
        }