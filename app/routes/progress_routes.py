from datetime import datetime

from flask import Blueprint
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from app.middleware.role_required import role_required
from app.extensions import db
from app.models.user import User, UserRole
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.models.module import Module
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.quiz import Quiz
from app.services.certificate_service import (
    is_course_completed,
    issue_certificate,
)
from app.services.quiz_service import has_passed_quiz

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

    existing = Progress.query.filter_by(
        student_id=user_id, lesson_id=lesson_id
    ).first()
    if existing:
        return jsonify({"message": "Already completed"}), 200

    quiz = Quiz.query.filter_by(lesson_id=lesson_id).first()
    if quiz and not has_passed_quiz(user_id, quiz):
        return jsonify({
            "message": "Pass the lesson quiz before marking this lesson complete"
        }), 400

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
    if is_course_completed(user_id, course.id):
        user = User.query.get(user_id)
        issue_certificate(
            user_id,
            course.id,
            student_name=user.name,
            course_name=course.title,
        )

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

    completed_progress_records = Progress.query.filter(
        Progress.student_id == user_id,
        Progress.lesson_id.in_(lesson_ids),
        Progress.completed == True
    ).all()

    completed_lessons = len(completed_progress_records)
    completed_lesson_ids = [p.lesson_id for p in completed_progress_records]

    percentage = 0

    if total_lessons > 0:
        percentage = (
            completed_lessons /
            total_lessons
        ) * 100

    return jsonify({
        "completed_lessons": [{"lesson_id": str(p.lesson_id)} for p in completed_progress_records],
        "progress_percentage": round(percentage, 2),
        "total_lessons": total_lessons,
        "completed_count": completed_lessons,
        # Keep existing fields for backward compatibility
        "course_id": course_id,
        "percentage": round(percentage, 2),
        "completed_lesson_ids": completed_lesson_ids
    })