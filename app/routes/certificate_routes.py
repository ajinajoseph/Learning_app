from flask import Blueprint
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from app.extensions import db

from app.middleware.role_required import role_required

from app.models.user import User
from app.models.user import UserRole

from app.models.course import Course
from app.models.module import Module
from app.models.lesson import Lesson

from app.models.progress import Progress
from app.models.certificate import Certificate

from app.services.certificate_service import (
    generate_certificate_url
)

certificate_bp = Blueprint(
    "certificate",
    __name__,
    url_prefix="/api/certificates"
)

@certificate_bp.route(
    "/generate/<course_id>",
    methods=["POST"]
)
@jwt_required()
@role_required(UserRole.STUDENT.value)
def generate_certificate(course_id):

    user_id = get_jwt_identity()

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

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

    lesson_ids = [
        lesson.id
        for lesson in lessons
    ]

    total_lessons = len(lesson_ids)

    completed = Progress.query.filter(
        Progress.student_id == user_id,
        Progress.lesson_id.in_(lesson_ids),
        Progress.completed == True
    ).count()

    if completed != total_lessons:

        return jsonify({
            "message":
            "Complete all lessons first"
        }), 400

    existing = Certificate.query.filter_by(
        student_id=user_id,
        course_id=course_id
    ).first()

    if existing:
        return jsonify(
            existing.to_dict()
        )

    user = User.query.get(user_id)

    certificate_url = generate_certificate_url(
        user.name,
        course.title
    )

    certificate = Certificate(
        student_id=user_id,
        course_id=course_id,
        certificate_url=certificate_url
    )

    db.session.add(certificate)

    db.session.commit()

    return jsonify(
        certificate.to_dict()
    ), 201

@certificate_bp.route("/my")
@jwt_required()
@role_required(UserRole.STUDENT.value)
def my_certificates():

    user_id = get_jwt_identity()

    certificates = Certificate.query.filter_by(
        student_id=user_id
    ).all()

    return jsonify([
        certificate.to_dict()
        for certificate in certificates
    ])


@certificate_bp.route("/<certificate_id>")
@jwt_required()
def get_certificate(certificate_id):

    certificate = Certificate.query.get(
        certificate_id
    )

    if not certificate:
        return jsonify({
            "message":
            "Certificate not found"
        }), 404

    return jsonify(
        certificate.to_dict()
    )