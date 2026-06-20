import uuid

from app.extensions import db


class Course(db.Model):

    __tablename__ = "courses"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    mentor_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False
    )

    mentor = db.relationship(
        "User",
        backref="courses"
    )

    is_approved = db.Column(
    db.Boolean,
    default=False,
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
        "description": self.description,
        "price": self.price,
        "mentor_id": self.mentor_id,
        "is_approved": self.is_approved
    }