from sqlalchemy import func

from app.extensions import db
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.quiz import Quiz
from app.services.quiz_service import quiz_summary_for_student


def next_sort_order(model, **filters):
    max_order = db.session.query(
        func.max(model.sort_order)
    ).filter_by(**filters).scalar()
    return (max_order or 0) + 1


def ordered_modules(course_id):
    return Module.query.filter_by(
        course_id=course_id,
    ).order_by(
        Module.sort_order.asc(),
        Module.created_at.asc(),
    ).all()


def ordered_lessons(module_id):
    return Lesson.query.filter_by(
        module_id=module_id,
    ).order_by(
        Lesson.sort_order.asc(),
        Lesson.created_at.asc(),
    ).all()


def build_lesson_payload(lesson, presign_media=False, student_id=None):
    data = lesson.to_dict(presign_media=presign_media)
    quiz = Quiz.query.filter_by(lesson_id=lesson.id).first()
    if quiz:
        if student_id:
            data["quiz"] = quiz_summary_for_student(student_id, quiz)
        else:
            data["quiz"] = quiz.to_dict()
    return data


def build_course_content(course_id, presign_media=False, student_id=None):
    module_data = []
    for module in ordered_modules(course_id):
        lessons = [
            build_lesson_payload(
                lesson,
                presign_media=presign_media,
                student_id=student_id,
            )
            for lesson in ordered_lessons(module.id)
        ]
        module_data.append({
            **module.to_dict(),
            "lessons": lessons,
        })
    return module_data
