import uuid

from app.extensions import db


class Certificate(db.Model):

    __tablename__ = "certificates"

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

    course_id = db.Column(
        db.String(36),
        db.ForeignKey("courses.id"),
        nullable=False
    )

    certificate_url = db.Column(
        db.String(500),
        nullable=False
    )

    issued_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):

        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "certificate_url": self.certificate_url,
            "issued_at": self.issued_at
        }