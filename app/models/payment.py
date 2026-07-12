import uuid

from app.extensions import db


import enum

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    FAILED = "failed"
class Payment(db.Model):

    __tablename__ = "payments"

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

    amount = db.Column(
        db.Float,
        nullable=False
    )

    provider = db.Column(
        db.String(20),
        nullable=False
    )

    transaction_id = db.Column(
        db.String(255)
    )

    status = db.Column(
    db.Enum(PaymentStatus),
    nullable=False,
    default=PaymentStatus.PENDING
    )
    

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    payment_intent_id = db.Column(
    db.String(255)
    )

    order_id = db.Column(
        db.String(255)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "amount": self.amount,
            "provider": self.provider,
            "transaction_id": self.transaction_id,
            "status": self.status.value,
        }