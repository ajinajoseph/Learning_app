from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import jwt_required
from app.services.s3_services import upload_file
from app.extensions import db
from flask_jwt_extended import get_jwt_identity

from app.models.course import Course
from app.models.user import UserRole

from app.middleware.role_required import role_required
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.enrollment import Enrollment
lesson_bp = Blueprint(
    "lesson",
    __name__,
    url_prefix="/api/lessons"
)

@lesson_bp.route("", methods=["POST"])
@jwt_required()
@role_required(UserRole.MENTOR)
def create_lesson():

    data = request.get_json()

    module = Module.query.get(
        data.get("module_id")
    )

    if not module:
        return jsonify({
            "message": "Module not found"
        }), 404

    lesson = Lesson(
        title=data["title"],
        content=data.get("content"),
        video_url=data.get("video_url"),
        pdf_url=data.get("pdf_url"),
        module_id=data["module_id"]
    )

    db.session.add(lesson)
    db.session.commit()

    from app.services.notification_service import (
        create_notification
    )

    enrollments = Enrollment.query.filter_by(
        course_id=module.course_id
    ).all()

    for enrollment in enrollments:

        create_notification(
            enrollment.student_id,
            "New Lesson Added",
            f"New lesson added: {lesson.title}"
        )

    return jsonify(
        lesson.to_dict()
    ), 201


@lesson_bp.route("/module/<module_id>")
def get_lessons(module_id):

    lessons = Lesson.query.filter_by(
        module_id=module_id
    ).all()

    return jsonify([
        lesson.to_dict()
        for lesson in lessons
    ])

@lesson_bp.route("/<lesson_id>")
def get_lesson(lesson_id):

    lesson = Lesson.query.get(
        lesson_id
    )

    if not lesson:
        return jsonify({
            "message": "Lesson not found"
        }), 404

    return jsonify(
        lesson.to_dict()
    )
@lesson_bp.route("/<lesson_id>", methods=["PUT"])
@jwt_required()
@role_required(UserRole.MENTOR)
def update_lesson(lesson_id):

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

    if course.mentor_id != user_id:
        return jsonify({
            "message": "Not your course"
        }), 403

    data = request.get_json()

    lesson.title = data.get(
        "title",
        lesson.title
    )

    lesson.content = data.get(
        "content",
        lesson.content
    )

    lesson.video_url = data.get(
        "video_url",
        lesson.video_url
    )

    lesson.pdf_url = data.get(
        "pdf_url",
        lesson.pdf_url
    )

    db.session.commit()

    return jsonify(
        lesson.to_dict()
    )
@lesson_bp.route("/<lesson_id>/upload-pdf", methods=["POST"])
@jwt_required()
@role_required(UserRole.MENTOR)
def upload_pdf(lesson_id):

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

    if course.mentor_id != user_id:
        return jsonify({
            "message": "Not your course"
        }), 403

    if "file" not in request.files:
        return jsonify({
            "message": "No file uploaded"
        }), 400

    file = request.files["file"]

    if not file.filename.endswith(".pdf"):
        return jsonify({
            "message": "Only PDF files allowed"
        }), 400

    url = upload_file(
        file,
        "lesson-pdfs"
    )

    lesson.pdf_url = url

    db.session.commit()

    return jsonify({
        "pdf_url": url
    })

@lesson_bp.route("/<lesson_id>/upload-video", methods=["POST"])
@jwt_required()
@role_required(UserRole.MENTOR)
def upload_video(lesson_id):

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

    if course.mentor_id != user_id:
        return jsonify({
            "message": "Not your course"
        }), 403

    if "file" not in request.files:
        return jsonify({
            "message": "No file uploaded"
        }), 400

    file = request.files["file"]

    allowed_extensions = (
        ".mp4",
        ".mov",
        ".avi"
    )

    if not file.filename.lower().endswith(
        allowed_extensions
    ):
        return jsonify({
            "message": "Invalid video format"
        }), 400

    url = upload_file(
        file,
        "lesson-videos"
    )

    lesson.video_url = url

    db.session.commit()

    return jsonify({
        "video_url": url
    })

@lesson_bp.route("/<lesson_id>", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.MENTOR)
def delete_lesson(lesson_id):

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

    if course.mentor_id != user_id:
        return jsonify({
            "message": "Not your course"
        }), 403

    db.session.delete(lesson)

    db.session.commit()

    return jsonify({
        "message": "Lesson deleted"
    })