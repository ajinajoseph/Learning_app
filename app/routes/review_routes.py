from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from app.extensions import db

from app.middleware.role_required import role_required

from app.models.review import Review
from app.models.enrollment import Enrollment


review_bp = Blueprint(
    "review",
    __name__,
    url_prefix="/api/reviews"
)


@review_bp.route("/<course_id>", methods=["POST"])
@jwt_required()
@role_required("student")
def create_review(course_id):

    user_id = get_jwt_identity()

    enrollment = Enrollment.query.filter_by(
        student_id=user_id,
        course_id=course_id
    ).first()

    if not enrollment:
        return jsonify({
            "message": "Enroll before reviewing"
        }), 403

    existing = Review.query.filter_by(
        student_id=user_id,
        course_id=course_id
    ).first()

    if existing:
        return jsonify({
            "message": "Review already submitted"
        }), 400

    data = request.get_json()

    rating = data.get("rating")

    if rating < 1 or rating > 5:
        return jsonify({
            "message": "Rating must be between 1 and 5"
        }), 400

    review = Review(
        course_id=course_id,
        student_id=user_id,
        rating=rating,
        comment=data.get("comment")
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({
        "message": "Review submitted"
    }), 201


@review_bp.route("/<course_id>", methods=["GET"])
def get_reviews(course_id):

    reviews = Review.query.filter_by(
        course_id=course_id
    ).all()

    return jsonify([
        review.to_dict()
        for review in reviews
    ])