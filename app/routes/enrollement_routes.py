from flask import Blueprint
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from app.extensions import db

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.user import User, UserRole
from app.middleware.role_required import role_required
from app.services.payment_service import has_completed_payment
from app.services.email_service import (
    send_email
)

enrollment_bp = Blueprint(
    "enrollment",
    __name__,
    url_prefix="/api/enrollments"
)


@enrollment_bp.route("/<course_id>", methods=["POST"])
@jwt_required()
@role_required(UserRole.STUDENT)
def enroll_course(course_id):

    user_id = get_jwt_identity()

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    if not course.is_approved:
        return jsonify({
            "message": "Course is not available for enrollment"
        }), 403

    existing = Enrollment.query.filter_by(
        student_id=user_id,
        course_id=course_id
    ).first()

    if existing:
        return jsonify({
            "message": "Already enrolled"
        }), 400

    if course.price > 0 and not has_completed_payment(user_id, course_id):
        return jsonify({
            "message": "Payment required before enrollment"
        }), 402

    enrollment = Enrollment(
        student_id=user_id,
        course_id=course_id
    )

    db.session.add(enrollment)
    db.session.commit()
    from app.services.notification_service import (
    create_notification
    )

    create_notification(
        course.mentor_id,
        "New Enrollment",
        f"A student enrolled in {course.title}"
    )
    mentor = User.query.get(
    course.mentor_id
)
    send_email(
        mentor.email,
        "New Enrollment",
        f"A student enrolled in '{course.title}'"
    )

    return jsonify({
        "message": "Enrollment successful"
    }), 201


@enrollment_bp.route("/my-courses", methods=["GET"])
@jwt_required()
@role_required(UserRole.STUDENT)
def my_courses():

    user_id = get_jwt_identity()

    enrollments = Enrollment.query.filter_by(
        student_id=user_id
    ).all()

    return jsonify([
        enrollment.to_dict()
        for enrollment in enrollments
    ])
