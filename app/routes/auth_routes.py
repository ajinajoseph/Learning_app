import re

from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
import random
import string
from datetime import datetime, timedelta
from flask import current_app

from app.models.user import User, UserRole


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


_otp_store = {}  # {email: {otp, expires_at}}


def _generate_otp():
    return ''.join(random.choices(string.digits, k=6))


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"message": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()

    # Always return success even if email not found
    # (security best practice — don't reveal if email exists)
    if user:
        otp = _generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        _otp_store[email] = {
            "otp": otp,
            "expires_at": expires_at,
            "verified": False
        }

        # Send OTP email
        try:
            from app.services.email_service import send_email
            send_email(
                recipient=email,
                subject="EduFlex — Password Reset OTP",
                body=f"""
Hi {user.name},

You requested a password reset for your EduFlex account.

Your OTP is: {otp}

This OTP is valid for 10 minutes.

If you did not request this, please ignore this email.

— The EduFlex Team
                """.strip()
            )
        except Exception as e:
            print(f"Failed to send OTP email: {e}")
            return jsonify({"message": "Failed to send OTP email"}), 500

    return jsonify({
        "message": "If this email is registered, an OTP has been sent."
    }), 200


@auth_bp.route("/verify-reset-otp", methods=["POST"])
def verify_reset_otp():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()

    if not email or not otp:
        return jsonify({"message": "Email and OTP are required"}), 400

    record = _otp_store.get(email)

    if not record:
        return jsonify({"message": "No OTP request found for this email"}), 400

    if datetime.utcnow() > record["expires_at"]:
        _otp_store.pop(email, None)
        return jsonify({"message": "OTP has expired. Please request a new one."}), 400

    if record["otp"] != otp:
        return jsonify({"message": "Invalid OTP"}), 400

    # Mark as verified so reset-password can proceed
    _otp_store[email]["verified"] = True

    return jsonify({"message": "OTP verified successfully"}), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if not email or not new_password or not confirm_password:
        return jsonify({"message": "All fields are required"}), 400

    if new_password != confirm_password:
        return jsonify({"message": "Passwords do not match"}), 400

    if len(new_password) < 8:
        return jsonify({
            "message": "Password must be at least 8 characters"
        }), 400

    record = _otp_store.get(email)
    if not record or not record.get("verified"):
        return jsonify({
            "message": "Please verify your OTP first"
        }), 400

    if datetime.utcnow() > record["expires_at"]:
        _otp_store.pop(email, None)
        return jsonify({"message": "Session expired. Please start over."}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    user.set_password(new_password)
    db.session.commit()

    # Clear OTP record after successful reset
    _otp_store.pop(email, None)

    return jsonify({"message": "Password reset successfully"}), 200

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name", "").strip()

    email = data.get("email", "").strip()

    password = data.get("password", "").strip()

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

    role_str = data.get("role", "student").strip().lower()

    try:
        role = UserRole(role_str)
    except ValueError:
        return jsonify({
            "message": "Invalid role"
        }), 400

    is_approved = False if role == UserRole.MENTOR else True

    user = User(
        name=name,
        email=email,
        role=role,
        is_approved=is_approved
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