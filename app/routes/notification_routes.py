from flask import Blueprint
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from app.extensions import db

from app.models.notification import Notification

from app.models.user import UserRole

from app.middleware.role_required import role_required


notification_bp = Blueprint(
    "notification",
    __name__,
    url_prefix="/api/notifications"
)


@notification_bp.route("")
@jwt_required()
@role_required(UserRole.STUDENT, UserRole.MENTOR, UserRole.ADMIN)
def get_notifications():

    user_id = get_jwt_identity()

    notifications = Notification.query.filter_by(
        user_id=user_id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return jsonify([
        notification.to_dict()
        for notification in notifications
    ])


@notification_bp.route(
    "/read/<notification_id>",
    methods=["PUT"]
)
@jwt_required()
@role_required(
    UserRole.STUDENT,
    UserRole.MENTOR,
    UserRole.ADMIN
)
def mark_read(notification_id):

    user_id = get_jwt_identity()

    notification = Notification.query.get(
        notification_id
    )

    if not notification:
        return jsonify({
            "message": "Notification not found"
        }), 404

    if notification.user_id != user_id:
        return jsonify({
            "message": "Access denied"
        }), 403

    notification.is_read = True

    db.session.commit()

    return jsonify({
        "message": "Notification marked as read"
    })


@notification_bp.route(
    "/unread-count"
)
@jwt_required()
@role_required(
    UserRole.STUDENT,
    UserRole.MENTOR,
    UserRole.ADMIN
)
def unread_count():

    user_id = get_jwt_identity()

    count = Notification.query.filter_by(
        user_id=user_id,
        is_read=False
    ).count()

    return jsonify({
        "unread_count": count
    })

