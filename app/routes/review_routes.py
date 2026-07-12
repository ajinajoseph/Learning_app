from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.middleware.role_required import role_required
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.review import Review, ReviewStatus
from app.models.review_report import ReportStatus, ReviewReport
from app.models.user import User, UserRole
from app.services.review_service import get_course_rating_stats
from app.services.elasticsearch_service import index_course


review_bp = Blueprint(
    "review",
    __name__,
    url_prefix="/api/reviews",
)


def _can_moderate_course(user, course):
    return (
        user.role == UserRole.ADMIN
        or (
            user.role == UserRole.MENTOR
            and course.mentor_id == user.id
        )
    )


@review_bp.route("/<course_id>", methods=["POST"])
@jwt_required()
@role_required(UserRole.STUDENT)
def create_review(course_id):
    user_id = get_jwt_identity()

    enrollment = Enrollment.query.filter_by(
        student_id=user_id,
        course_id=course_id,
    ).first()

    if not enrollment:
        return jsonify({"message": "Enroll before reviewing"}), 403

    existing = Review.query.filter_by(
        student_id=user_id,
        course_id=course_id,
    ).first()

    if existing:
        return jsonify({"message": "Review already submitted"}), 400

    data = request.get_json() or {}
    rating = data.get("rating")

    if rating is None or rating < 1 or rating > 5:
        return jsonify({"message": "Rating must be between 1 and 5"}), 400

    review = Review(
        course_id=course_id,
        student_id=user_id,
        rating=rating,
        comment=data.get("comment"),
        status=ReviewStatus.APPROVED,
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({
        "message": "Review submitted successfully",
        "review": review.to_dict(),
    }), 201


@review_bp.route("/<course_id>", methods=["GET"])
def get_reviews(course_id):
    reviews = Review.query.filter(
        Review.course_id == course_id,
        Review.status != ReviewStatus.REJECTED
    ).order_by(Review.created_at.desc()).all()

    return jsonify({
        "reviews": [r.to_dict() for r in reviews],
        "total": len(reviews),
        "rating_stats": get_course_rating_stats(course_id),
    }), 200


@review_bp.route("/<review_id>/report", methods=["POST"])
@jwt_required()
@role_required(UserRole.STUDENT)
def report_review(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get(review_id)

    if not review:
        return jsonify({"message": "Review not found"}), 404

    if review.student_id == user_id:
        return jsonify({"message": "You cannot report your own review"}), 400

    data = request.get_json() or {}
    reason = data.get("reason", "").strip()

    if not reason:
        return jsonify({"message": "Report reason is required"}), 400

    existing = ReviewReport.query.filter_by(
        review_id=review_id,
        reporter_id=user_id,
    ).first()

    if existing:
        return jsonify({"message": "You already reported this review"}), 400

    report = ReviewReport(
        review_id=review_id,
        reporter_id=user_id,
        reason=reason,
        status=ReportStatus.PENDING,
    )

    db.session.add(report)
    db.session.commit()

    return jsonify({
        "message": "Review reported successfully",
        "report": report.to_dict(),
    }), 201


@review_bp.route("/<review_id>/moderate", methods=["PUT"])
@jwt_required()
@role_required(UserRole.ADMIN, UserRole.MENTOR)
def moderate_review(review_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    review = Review.query.get(review_id)

    if not review:
        return jsonify({"message": "Review not found"}), 404

    course = Course.query.get(review.course_id)
    if not course or not _can_moderate_course(user, course):
        return jsonify({"message": "Access denied"}), 403

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
    index_course(course)

    return jsonify({
        "message": f"Review {action}d",
        "review": review.to_dict(),
        "rating_stats": get_course_rating_stats(review.course_id),
    }), 200


@review_bp.route("/pending/<course_id>", methods=["GET"])
@jwt_required()
@role_required(UserRole.ADMIN, UserRole.MENTOR)
def pending_reviews(course_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    course = Course.query.get(course_id)

    if not course:
        return jsonify({"message": "Course not found"}), 404

    if not _can_moderate_course(user, course):
        return jsonify({"message": "Access denied"}), 403

    reviews = Review.query.filter_by(
        course_id=course_id,
        status=ReviewStatus.PENDING,
    ).all()

    return jsonify([review.to_dict() for review in reviews]), 200
