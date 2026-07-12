from flask import Blueprint
from flask import jsonify
from flask import request

from flask_jwt_extended import jwt_required

from app.extensions import db

from app.models.user import User
from app.models.user import UserRole

from app.models.course import Course
from app.models.review import Review, ReviewStatus
from app.models.review_report import ReportStatus, ReviewReport
from app.models.enrollment import Enrollment

from app.middleware.role_required import role_required

from app.services.notification_service import (
    create_notification
)
from app.services.email_service import (
    send_email
)
from app.services.review_service import get_course_rating_stats
from app.services.elasticsearch_service import (
    delete_course_from_index,
    index_course,
)

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


@admin_bp.route("/users")
@jwt_required()
@role_required(UserRole.ADMIN)
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
@role_required(UserRole.ADMIN)
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

    if user.role == UserRole.MENTOR:
        user.is_approved = False
    else:
        user.is_approved = True

    db.session.commit()

    return jsonify({
        "message": "Role updated",
        "role": user.role.value
    })


@admin_bp.route("/courses")
@jwt_required()
@role_required(UserRole.ADMIN)
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
@role_required(UserRole.ADMIN)
def approve_course(course_id):

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    course.is_approved = True

    db.session.commit()
    index_course(course)

    create_notification(
        course.mentor_id,
        "Course Approved",
        f"Your course '{course.title}' has been approved."
    )
    send_email(
        course.mentor.email,
        "Course Approved",
        f"Your course '{course.title}' has been approved."
    )


    return jsonify({
        "message": "Course approved successfully"
    })


@admin_bp.route(
    "/courses/<course_id>/reject",
    methods=["PUT"]
)
@jwt_required()
@role_required(UserRole.ADMIN)
def reject_course(course_id):

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    course.is_approved = False

    db.session.commit()
    delete_course_from_index(course_id)

    create_notification(
        course.mentor_id,
        "Course Rejected",
        f"Your course '{course.title}' was rejected and is no longer published.",
    )
    send_email(
        course.mentor.email,
        "Course Rejected",
        f"Your course '{course.title}' was rejected and is no longer published.",
    )

    return jsonify({
        "message": "Course rejected successfully"
    })


@admin_bp.route("/mentors/pending")
@jwt_required()
@role_required(UserRole.ADMIN)
def pending_mentors():

    mentors = User.query.filter_by(
        role=UserRole.MENTOR,
        is_approved=False,
    ).all()

    return jsonify([
        user.to_dict()
        for user in mentors
    ])


@admin_bp.route(
    "/mentors/<user_id>/approve",
    methods=["PUT"]
)
@jwt_required()
@role_required(UserRole.ADMIN)
def approve_mentor(user_id):

    user = User.query.get(user_id)

    if not user or user.role != UserRole.MENTOR:
        return jsonify({"message": "Mentor not found"}), 404

    user.is_approved = True
    db.session.commit()

    create_notification(
        user.id,
        "Mentor Approved",
        "Your mentor account has been approved.",
    )
    send_email(
        user.email,
        "Mentor Approved",
        "Your mentor account has been approved. You can now create courses.",
    )

    return jsonify({
        "message": "Mentor approved successfully",
        "user": user.to_dict(),
    })


@admin_bp.route(
    "/mentors/<user_id>/reject",
    methods=["PUT"]
)
@jwt_required()
@role_required(UserRole.ADMIN)
def reject_mentor(user_id):

    user = User.query.get(user_id)

    if not user or user.role != UserRole.MENTOR:
        return jsonify({"message": "Mentor not found"}), 404

    user.is_approved = False
    db.session.commit()

    create_notification(
        user.id,
        "Mentor Application Rejected",
        "Your mentor account application was not approved.",
    )
    send_email(
        user.email,
        "Mentor Application Rejected",
        "Your mentor account application was not approved.",
    )

    return jsonify({
        "message": "Mentor rejected successfully",
        "user": user.to_dict(),
    })


@admin_bp.route(
    "/courses/<course_id>",
    methods=["DELETE"]
)
@jwt_required()
@role_required(UserRole.ADMIN)
def delete_course(course_id):

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    db.session.delete(course)
    db.session.commit()
    delete_course_from_index(course_id)

    return jsonify({
        "message": "Course deleted"
    })


@admin_bp.route(
    "/reviews/<review_id>",
    methods=["DELETE"]
)
@jwt_required()
@role_required(UserRole.ADMIN)
def delete_review(review_id):

    review = Review.query.get(review_id)

    if not review:
        return jsonify({
            "message": "Review not found"
        }), 404

    ReviewReport.query.filter_by(review_id=review_id).delete()
    course_id = review.course_id
    db.session.delete(review)
    db.session.commit()

    course = Course.query.get(course_id)
    if course:
        index_course(course)

    return jsonify({
        "message": "Review deleted"
    })


@admin_bp.route(
    "/reviews/<review_id>/moderate",
    methods=["PUT"]
)
@jwt_required()
@role_required(UserRole.ADMIN)
def admin_moderate_review(review_id):

    review = Review.query.get(review_id)

    if not review:
        return jsonify({"message": "Review not found"}), 404

    data = request.get_json() or {}
    action = data.get("action")

    if action == "approve":
        review.status = ReviewStatus.APPROVED
    elif action == "reject":
        review.status = ReviewStatus.REJECTED
    else:
        return jsonify({
            "message": "action must be 'approve' or 'reject'",
        }), 400

    db.session.commit()

    course = Course.query.get(review.course_id)
    if course:
        index_course(course)

    return jsonify({
        "message": f"Review {action}d",
        "review": review.to_dict(),
        "rating_stats": get_course_rating_stats(review.course_id),
    })


@admin_bp.route("/review-reports", methods=["GET"])
@jwt_required()
@role_required(UserRole.ADMIN)
def get_review_reports():

    reports = ReviewReport.query.filter_by(
        status=ReportStatus.PENDING,
    ).all()

    return jsonify([report.to_dict() for report in reports])


@admin_bp.route(
    "/review-reports/<report_id>",
    methods=["PUT"]
)
@jwt_required()
@role_required(UserRole.ADMIN)
def resolve_review_report(report_id):

    report = ReviewReport.query.get(report_id)

    if not report:
        return jsonify({"message": "Report not found"}), 404

    data = request.get_json() or {}
    action = data.get("action")

    if action == "resolve":
        report.status = ReportStatus.RESOLVED
        review = Review.query.get(report.review_id)
        if review:
            review.status = ReviewStatus.REJECTED
    elif action == "dismiss":
        report.status = ReportStatus.DISMISSED
    else:
        return jsonify({
            "message": "action must be 'resolve' or 'dismiss'",
        }), 400

    db.session.commit()

    review = Review.query.get(report.review_id)
    if review:
        course = Course.query.get(review.course_id)
        if course:
            index_course(course)

    return jsonify({
        "message": f"Report {action}d",
        "report": report.to_dict(),
    })


@admin_bp.route("/dashboard")
@jwt_required()
@role_required(UserRole.ADMIN)
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

    pending_mentors = User.query.filter_by(
        role=UserRole.MENTOR,
        is_approved=False,
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

        "pending_mentors":
        pending_mentors,

        "total_reviews":
        total_reviews,

        "total_enrollments":
        total_enrollments
    })