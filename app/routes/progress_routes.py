from datetime import datetime

from flask import Blueprint
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from app.middleware.role_required import role_required
from app.extensions import db
from app.models.user import UserRole
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.models.module import Module
from app.models.course import Course
from app.models.enrollment import Enrollment

progress_bp = Blueprint(
    "progress",
    __name__,
    url_prefix="/api/progress"
)


@progress_bp.route("/complete/<lesson_id>", methods=["POST"])
@jwt_required()
@role_required(UserRole.STUDENT)
def complete_lesson(lesson_id):

    user_id = get_jwt_identity()

    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({
            "message": "Lesson not found"
        }), 404
    module = Module.query.get(
    lesson.module_id
)

    course = Course.query.get(
        module.course_id
    )

    enrollment = Enrollment.query.filter_by(
        student_id=user_id,
        course_id=course.id
    ).first()

    if not enrollment:
        return jsonify({
            "message": "You are not enrolled in this course"
        }), 403
    progress = Progress.query.filter_by(
        student_id=user_id,
        lesson_id=lesson_id
    ).first()

    if not progress:
        progress = Progress(
            student_id=user_id,
            lesson_id=lesson_id,
            completed=True,
            completed_at=datetime.utcnow()
        )

        db.session.add(progress)

    else:
        progress.completed = True
        progress.completed_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "message": "Lesson marked completed"
    })

@progress_bp.route("/course/<course_id>")
@jwt_required()
@role_required(UserRole.STUDENT)
def get_course_progress(course_id):

    user_id = get_jwt_identity()

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404
    enrollment = Enrollment.query.filter_by(
    student_id=user_id,
    course_id=course_id
    ).first()

    if not enrollment:
        return jsonify({
            "message": "You are not enrolled in this course"
        }), 403
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

    completed_lessons = Progress.query.filter(
        Progress.student_id == user_id,
        Progress.lesson_id.in_(lesson_ids),
        Progress.completed == True
    ).count()

    percentage = 0

    if total_lessons > 0:
        percentage = (
            completed_lessons /
            total_lessons
        ) * 100

    return jsonify({
        "course_id": course_id,
        "completed_lessons": completed_lessons,
        "total_lessons": total_lessons,
        "percentage": round(percentage, 2)
    })