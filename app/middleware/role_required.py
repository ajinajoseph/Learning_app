from functools import wraps

from flask import jsonify

from flask_jwt_extended import get_jwt_identity

from app.models.user import User


def role_required(*roles):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            user_id = get_jwt_identity()

            user = User.query.get(user_id)

            if not user:
                return jsonify({
                    "message": "User not found"
                }), 404

            if user.role.value not in roles:
                return jsonify({
                    "message": "Access denied"
                }), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator