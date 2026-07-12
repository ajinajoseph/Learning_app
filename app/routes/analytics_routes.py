from flask import Blueprint
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from sqlalchemy import func

from app.extensions import db

from app.middleware.role_required import role_required

from app.models.user import User
from app.models.user import UserRole

from app.models.course import Course
from app.models.module import Module
from app.models.lesson import Lesson

from app.models.progress import Progress
from app.models.review import Review, ReviewStatus
from app.services.review_service import (
    calculate_average_rating,
    calculate_weighted_rating,
)
from app.models.enrollment import Enrollment


analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/api/analytics"
)


@analytics_bp.route(
    "/course/<course_id>"
)
@jwt_required()
@role_required(UserRole.ADMIN, UserRole.MENTOR)
def course_analytics(course_id):

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    if (
        user.role != UserRole.ADMIN
        and
        course.mentor_id != user_id
    ):
        return jsonify({
            "message": "Access denied"
        }), 403

    total_students = Enrollment.query.filter_by(
        course_id=course_id
    ).count()

    total_reviews = Review.query.filter_by(
        course_id=course_id,
        status=ReviewStatus.APPROVED,
    ).count()

    average_rating = calculate_average_rating(course_id)
    weighted_rating = calculate_weighted_rating(course_id)

    modules = Module.query.filter_by(
        course_id=course_id
    ).all()

    module_ids = [
        module.id
        for module in modules
    ]

    lessons = Lesson.query.filter(
        Lesson.module_id.in_(module_ids)
    ).all()

    total_lessons = len(lessons)

    lesson_ids = [
        lesson.id
        for lesson in lessons
    ]

    completed_progress = Progress.query.filter(
        Progress.lesson_id.in_(lesson_ids),
        Progress.completed == True
    ).count()

    completion_rate = 0

    if (
        total_students > 0
        and
        total_lessons > 0
    ):
        completion_rate = (
            completed_progress
            /
            (
                total_students
                * total_lessons
            )
        ) * 100

    return jsonify({

        "course_id": course_id,

        "total_students": total_students,

        "total_reviews": total_reviews,

        "average_rating": average_rating,

        "weighted_rating": weighted_rating,

        "completion_rate": round(
            completion_rate,
            2
        )
    })