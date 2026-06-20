import re

from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from app.extensions import db

from app.models.user import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

PASSWORD_REGEX = (
    r'^(?=.*[a-z])'
    r'(?=.*[A-Z])'
    r'(?=.*\d)'
    r'(?=.*[@$!%*?&])'
    r'[A-Za-z\d@$!%*?&]{8,}$'
)


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name", "").strip()

    email = data.get("email", "").strip()

    password = data.get("password", "").strip()

    role = data.get("role", "student")

    if not name:
        return jsonify({
            "message": "Name required"
        }), 400

    if not re.match(
        EMAIL_REGEX,
        email
    ):
        return jsonify({
            "message": "Invalid email"
        }), 400

    if not re.match(
        PASSWORD_REGEX,
        password
    ):
        return jsonify({
            "message":
            "Password must contain uppercase, lowercase, number and special character"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "message": "Email already exists"
        }), 400

    user = User(
        name=name,
        email=email,
        role=role
    )

    user.set_password(password)

    db.session.add(user)

    db.session.commit()

    return jsonify({
        "message": "User registered successfully"
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email", "").strip()

    password = data.get("password", "").strip()

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:
        return jsonify({
            "message": "Invalid credentials"
        }), 401

    if not user.check_password(password):
        return jsonify({
            "message": "Invalid credentials"
        }), 401

    access_token = create_access_token(
        identity=user.id
    )

    refresh_token = create_refresh_token(
        identity=user.id
    )

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }), 200
@auth_bp.route("/profile")
@jwt_required()
def profile():

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    return jsonify(
        user.to_dict()
    )

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    user_id = get_jwt_identity()

    access_token = create_access_token(
        identity=user_id
    )

    return jsonify({
        "access_token": access_token
    })