import uuid

from app.extensions import db


class LessonAttachment(db.Model):

    __tablename__ = "lesson_attachments"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    lesson_id = db.Column(
        db.String(36),
        db.ForeignKey("lessons.id"),
        nullable=False,
    )

    title = db.Column(
        db.String(200),
        nullable=False,
    )

    file_key = db.Column(
        db.String(500),
        nullable=False,
    )

    file_type = db.Column(
        db.String(50),
        nullable=True,
    )

    sort_order = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
    )

    def to_dict(self, presign=False):
        from app.services.s3_services import resolve_media_url

        return {
            "id": self.id,
            "lesson_id": self.lesson_id,
            "title": self.title,
            "file_type": self.file_type,
            "sort_order": self.sort_order,
            "file_url": resolve_media_url(self.file_key) if presign else self.file_key,
            "created_at": self.created_at,
        }
