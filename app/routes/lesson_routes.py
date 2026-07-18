import os

from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from app.models.course import Course
from app.models.user import User, UserRole
from app.middleware.role_required import role_required
from app.middleware.mentor_approved import approved_mentor_required
from app.models.lesson import Lesson
from app.models.lesson_attachment import LessonAttachment
from app.models.module import Module
from app.models.enrollment import Enrollment
from app.services.course_access import (
    get_course_id_for_lesson,
    get_course_id_for_module,
    user_has_course_access,
)
from app.services.curriculum_service import next_sort_order, ordered_lessons
from app.services.s3_services import upload_file, resolve_media_url
from app.services.email_service import send_email
from app.extensions import db
from app.services.s3_services import (
    upload_file,
    generate_presigned_url,
)

lesson_bp = Blueprint(
    "lesson",
    __name__,
    url_prefix="/api/lessons"
)

ALLOWED_ATTACHMENT_EXTENSIONS = (
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".zip",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
)


def _mentor_owns_lesson(user_id, lesson):
    module = Module.query.get(lesson.module_id)
    course = Course.query.get(module.course_id)
    return course.mentor_id == user_id


@lesson_bp.route("", methods=["POST"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
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
        module_id=data["module_id"],
        sort_order=data.get(
            "sort_order",
            next_sort_order(Lesson, module_id=data["module_id"]),
        ),
    )

    db.session.add(lesson)
    db.session.commit()

    from app.services.notification_service import create_notification

    enrollments = Enrollment.query.filter_by(
        course_id=module.course_id
    ).all()
    course = Course.query.get(module.course_id)

    for enrollment in enrollments:
        create_notification(
            enrollment.student_id,
            "New Lesson Added",
            f"New lesson added: {lesson.title}"
        )
        student = User.query.get(enrollment.student_id)
        send_email(
            student.email,
            "New Lesson Added",
            f"'{lesson.title}' was added to '{course.title}'"
        )

    return jsonify(
        lesson.to_dict()
    ), 201


@lesson_bp.route("/module/<module_id>")
@jwt_required()
def get_lessons(module_id):

    user_id = get_jwt_identity()
    course_id = get_course_id_for_module(module_id)

    if not course_id:
        return jsonify({"message": "Module not found"}), 404

    if not user_has_course_access(user_id, course_id):
        return jsonify({"message": "Access denied"}), 403

    return jsonify([
        lesson.to_dict(presign_media=True)
        for lesson in ordered_lessons(module_id)
    ])


@lesson_bp.route("/<lesson_id>")
@jwt_required()
def get_lesson(lesson_id):

    user_id = get_jwt_identity()
    course_id = get_course_id_for_lesson(lesson_id)

    if not course_id:
        return jsonify({
            "message": "Lesson not found"
        }), 404

    if not user_has_course_access(user_id, course_id):
        return jsonify({"message": "Access denied"}), 403

    lesson = Lesson.query.get(lesson_id)

    return jsonify(
        lesson.to_dict(presign_media=True)
    )


@lesson_bp.route("/<lesson_id>", methods=["PUT"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def update_lesson(lesson_id):

    user_id = get_jwt_identity()

    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({
            "message": "Lesson not found"
        }), 404

    if not _mentor_owns_lesson(user_id, lesson):
        return jsonify({
            "message": "Not your course"
        }), 403

    data = request.get_json()

    lesson.title = data.get("title", lesson.title)
    lesson.content = data.get("content", lesson.content)
    if "video_url" in data:
       lesson.video_url = data["video_url"]
    if "pdf_url" in data:
        lesson.pdf_url = data["pdf_url"]
    if "sort_order" in data:
        lesson.sort_order = data["sort_order"]

    db.session.commit()

    return jsonify(
        lesson.to_dict()
    )


@lesson_bp.route("/<lesson_id>/attachments", methods=["POST"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def upload_attachment(lesson_id):

    user_id = get_jwt_identity()
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({"message": "Lesson not found"}), 404

    if not _mentor_owns_lesson(user_id, lesson):
        return jsonify({"message": "Not your course"}), 403

    if "file" not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename or ""
    extension = os.path.splitext(filename)[1].lower()

    if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
        return jsonify({"message": "Unsupported file type"}), 400

    title = request.form.get("title") or filename
    file_key = upload_file(file, "lesson-attachments")

    attachment = LessonAttachment(
        lesson_id=lesson_id,
        title=title,
        file_key=file_key,
        file_type=extension.lstrip("."),
        sort_order=next_sort_order(
            LessonAttachment,
            lesson_id=lesson_id,
        ),
    )

    db.session.add(attachment)
    db.session.commit()

    return jsonify(attachment.to_dict(presign=True)), 201


@lesson_bp.route(
    "/<lesson_id>/attachments/<attachment_id>",
    methods=["DELETE"],
)
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def delete_attachment(lesson_id, attachment_id):

    user_id = get_jwt_identity()
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({"message": "Lesson not found"}), 404

    if not _mentor_owns_lesson(user_id, lesson):
        return jsonify({"message": "Not your course"}), 403

    attachment = LessonAttachment.query.filter_by(
        id=attachment_id,
        lesson_id=lesson_id,
    ).first()

    if not attachment:
        return jsonify({"message": "Attachment not found"}), 404

    db.session.delete(attachment)
    db.session.commit()

    return jsonify({"message": "Attachment deleted"})


@lesson_bp.route("/<lesson_id>/upload-pdf", methods=["POST"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def upload_pdf(lesson_id):

    user_id = get_jwt_identity()
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({"message": "Lesson not found"}), 404

    if not _mentor_owns_lesson(user_id, lesson):
        return jsonify({"message": "Not your course"}), 403

    if "file" not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files["file"]

    if not file.filename.endswith(".pdf"):
        return jsonify({"message": "Only PDF files allowed"}), 400

        # Upload directly to S3
    file_key = upload_file(file, "pdfs")

    lesson.pdf_url = file_key
    db.session.commit()

    return jsonify({
        "pdf_url": generate_presigned_url(file_key),
        "message": "Uploaded"
    })

@lesson_bp.route("/<lesson_id>/upload-video", methods=["POST"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def upload_video(lesson_id):

    user_id = get_jwt_identity()
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({"message": "Lesson not found"}), 404

    if not _mentor_owns_lesson(user_id, lesson):
        return jsonify({"message": "Not your course"}), 403

    if "file" not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files["file"]
    allowed_extensions = (".mp4", ".mov", ".avi")

    if not file.filename.lower().endswith(allowed_extensions):
        return jsonify({"message": "Invalid video format"}), 400

    # Upload directly to S3
    file_key = upload_file(file, "videos")

    lesson.video_url = file_key
    db.session.commit()

    return jsonify({
        "video_url": generate_presigned_url(file_key),
        "message": "Uploaded"
    })
@lesson_bp.route("/<lesson_id>/video", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def delete_video(lesson_id):

    user_id = get_jwt_identity()
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({"message": "Lesson not found"}), 404

    if not _mentor_owns_lesson(user_id, lesson):
        return jsonify({"message": "Not your course"}), 403

    lesson.video_url = None
    db.session.commit()

    return jsonify({"message": "Video removed"})

@lesson_bp.route("/<lesson_id>/pdf", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def delete_pdf(lesson_id):

    user_id = get_jwt_identity()
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({"message": "Lesson not found"}), 404

    if not _mentor_owns_lesson(user_id, lesson):
        return jsonify({"message": "Not your course"}), 403

    lesson.pdf_url = None
    db.session.commit()

    return jsonify({"message": "PDF removed"})

@lesson_bp.route("/<lesson_id>", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def delete_lesson(lesson_id):

    user_id = get_jwt_identity()
    lesson = Lesson.query.get(lesson_id)

    if not lesson:
        return jsonify({"message": "Lesson not found"}), 404

    if not _mentor_owns_lesson(user_id, lesson):
        return jsonify({"message": "Not your course"}), 403

    db.session.delete(lesson)
    db.session.commit()

    return jsonify({"message": "Lesson deleted"})
