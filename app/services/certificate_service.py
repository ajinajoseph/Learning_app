import uuid

from app.extensions import db

from app.models.progress import Progress
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.certificate import Certificate
from app.models.quiz import Quiz
from app.services.certificate_pdf import generate_certificate_pdf
from app.services.quiz_service import has_passed_quiz
from app.services.s3_services import upload_fileobj


def is_course_completed(student_id, course_id):

    modules = Module.query.filter_by(
        course_id=course_id
    ).all()

    module_ids = [m.id for m in modules]

    lessons = Lesson.query.filter(
        Lesson.module_id.in_(module_ids)
    ).all()

    lesson_ids = [l.id for l in lessons]

    if not lesson_ids:
        return False

    completed_lessons = Progress.query.filter(
        Progress.student_id == student_id,
        Progress.lesson_id.in_(lesson_ids),
        Progress.completed == True
    ).count()

    if completed_lessons != len(lesson_ids):
        return False

    quizzes = Quiz.query.filter(
        Quiz.lesson_id.in_(lesson_ids)
    ).all()

    for quiz in quizzes:
        if not has_passed_quiz(student_id, quiz):
            return False

    return True


def issue_certificate(student_id, course_id, student_name, course_name):

    existing = Certificate.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()

    if existing:
        return existing

    certificate_id = str(uuid.uuid4())

    pdf_buffer = generate_certificate_pdf(
        student_name=student_name,
        course_name=course_name,
        certificate_id=certificate_id
    )

    filename = f"certificate_{certificate_id}.pdf"
    certificate_url = upload_fileobj(pdf_buffer, filename)
    certificate = Certificate(
        id=certificate_id,
        student_id=student_id,
        course_id=course_id,
        certificate_url=certificate_url
    )

    db.session.add(certificate)
    db.session.commit()

    return certificate
