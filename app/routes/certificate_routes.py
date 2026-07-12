from flask import Blueprint
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from app.middleware.role_required import role_required
from app.models.user import User, UserRole
from app.models.course import Course

from app.models.certificate import Certificate
from app.services.certificate_service import (
    is_course_completed,
    issue_certificate
)

from app.models.enrollment import Enrollment
from app.services.s3_services import resolve_media_url

certificate_bp = Blueprint(
    "certificate",
    __name__,
    url_prefix="/api/certificates"
)

@certificate_bp.route("/my")
@jwt_required()
@role_required(UserRole.STUDENT)
def my_certificates():

    user_id = get_jwt_identity()

    certificates = Certificate.query.filter_by(
        student_id=user_id
    ).all()

    return jsonify([
        _certificate_dict(certificate)
        for certificate in certificates
    ])

@certificate_bp.route("/generate/<course_id>", methods=["POST"])
@jwt_required()
@role_required(UserRole.STUDENT)
def generate_certificate(course_id):

    user_id = get_jwt_identity()

    enrollment = Enrollment.query.filter_by(
        student_id=user_id,
        course_id=course_id
    ).first()

    if not enrollment:
        return jsonify({
            "message": "Not enrolled in course"
        }), 403

    completed = is_course_completed(
        user_id,
        course_id
    )

    if not completed:
        return jsonify({
            "message": "Course not completed"
        }), 400

    user = User.query.get(user_id)
    course = Course.query.get(course_id)

    certificate = issue_certificate(
        user_id,
        course_id,
        student_name=user.name,
        course_name=course.title,
    )
    return jsonify(
        _certificate_dict(certificate)
    ), 201

@certificate_bp.route("/<certificate_id>")
def get_certificate(certificate_id):

    certificate = Certificate.query.get(
        certificate_id
    )

    if not certificate:
        return jsonify({
            "message": "Not found"
        }), 404

    return jsonify(
        _certificate_dict(certificate)
    )


def _certificate_dict(certificate):
    data = certificate.to_dict()
    data["certificate_url"] = resolve_media_url(
        certificate.certificate_url
    )
    return data
