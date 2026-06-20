from flask import Blueprint
from flask import jsonify
from flask import request

from flask_jwt_extended import jwt_required

from app.extensions import db

from app.models.user import User
from app.models.user import UserRole

from app.models.course import Course
from app.models.review import Review
from app.models.enrollment import Enrollment

from app.middleware.role_required import role_required

from app.services.notification_service import (
    create_notification
)

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


@admin_bp.route("/users")
@jwt_required()
@role_required(UserRole.ADMIN.value)
def get_users():

    users = User.query.all()

    return jsonify([
        user.to_dict()
        for user in users
    ])


@admin_bp.route(
    "/users/<user_id>/role",
    methods=["PUT"]
)
@jwt_required()
@role_required(UserRole.ADMIN.value)
def change_role(user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    data = request.get_json()

    role = data.get("role")

    valid_roles = [
        UserRole.STUDENT.value,
        UserRole.MENTOR.value,
        UserRole.ADMIN.value
    ]

    if role not in valid_roles:
        return jsonify({
            "message": "Invalid role"
        }), 400

    user.role = UserRole(role)

    db.session.commit()

    return jsonify({
        "message": "Role updated",
        "role": user.role.value
    })


@admin_bp.route("/courses")
@jwt_required()
@role_required(UserRole.ADMIN.value)
def get_all_courses():

    courses = Course.query.all()

    return jsonify([
        course.to_dict()
        for course in courses
    ])


@admin_bp.route(
    "/courses/<course_id>/approve",
    methods=["PUT"]
)
@jwt_required()
@role_required(UserRole.ADMIN.value)
def approve_course(course_id):

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    course.is_approved = True

    db.session.commit()

    create_notification(
        course.mentor_id,
        "Course Approved",
        f"Your course '{course.title}' has been approved."
    )

    return jsonify({
        "message": "Course approved successfully"
    })


@admin_bp.route(
    "/courses/<course_id>",
    methods=["DELETE"]
)
@jwt_required()
@role_required(UserRole.ADMIN.value)
def delete_course(course_id):

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    db.session.delete(course)

    db.session.commit()

    return jsonify({
        "message": "Course deleted"
    })


@admin_bp.route(
    "/reviews/<review_id>",
    methods=["DELETE"]
)
@jwt_required()
@role_required(UserRole.ADMIN.value)
def delete_review(review_id):

    review = Review.query.get(review_id)

    if not review:
        return jsonify({
            "message": "Review not found"
        }), 404

    db.session.delete(review)

    db.session.commit()

    return jsonify({
        "message": "Review deleted"
    })


@admin_bp.route("/dashboard")
@jwt_required()
@role_required(UserRole.ADMIN.value)
def dashboard():

    total_users = User.query.count()

    total_students = User.query.filter_by(
        role=UserRole.STUDENT
    ).count()

    total_mentors = User.query.filter_by(
        role=UserRole.MENTOR
    ).count()

    total_courses = Course.query.count()

    approved_courses = Course.query.filter_by(
        is_approved=True
    ).count()

    total_reviews = Review.query.count()

    total_enrollments = Enrollment.query.count()

    return jsonify({

        "total_users":
        total_users,

        "total_students":
        total_students,

        "total_mentors":
        total_mentors,

        "total_courses":
        total_courses,

        "approved_courses":
        approved_courses,

        "total_reviews":
        total_reviews,

        "total_enrollments":
        total_enrollments
    })