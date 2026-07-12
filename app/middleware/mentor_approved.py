from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from app.models.user import User, UserRole


def approved_mentor_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"message": "User not found"}), 404

        if user.role == UserRole.ADMIN:
            return func(*args, **kwargs)

        if user.role == UserRole.MENTOR and user.is_approved:
            return func(*args, **kwargs)

        return jsonify({
            "message": "Mentor account pending admin approval",
        }), 403

    return wrapper
