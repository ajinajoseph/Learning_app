from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from app.extensions import db

from app.models.course import Course
from app.models.announcement import Announcement
from app.models.enrollment import Enrollment

from app.models.user import User
from app.models.user import UserRole

from app.middleware.role_required import role_required
from app.middleware.mentor_approved import approved_mentor_required

from app.services.notification_service import (
    create_notification
)

announcement_bp = Blueprint(
    "announcement",
    __name__,
    url_prefix="/api/announcements"
)
@announcement_bp.route("", methods=["POST"])
@jwt_required()
@role_required(
    UserRole.MENTOR,
    UserRole.ADMIN,
)
@approved_mentor_required
def create_announcement():

    user_id = get_jwt_identity()

    data = request.get_json()

    course = Course.query.get(
        data["course_id"]
    )

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    user = User.query.get(user_id)

    if (
        user.role != UserRole.ADMIN
        and
        course.mentor_id != user_id
    ):
        return jsonify({
            "message": "Access denied"
        }), 403

    announcement = Announcement(
        course_id=data["course_id"],
        title=data["title"],
        message=data["message"]
    )

    db.session.add(announcement)

    enrollments = Enrollment.query.filter_by(
        course_id=course.id
    ).all()

    for enrollment in enrollments:

        create_notification(
            enrollment.student_id,
            announcement.title,
            announcement.message
        )

    db.session.commit()

    return jsonify(
        announcement.to_dict()
    ), 201

@announcement_bp.route("/<announcement_id>", methods=["PUT"])
@jwt_required()
@role_required(
    UserRole.MENTOR,
    UserRole.ADMIN,
)
@approved_mentor_required
def update_announcement(announcement_id):
    user_id = get_jwt_identity()
    announcement = Announcement.query.get_or_404(announcement_id)
    course = Course.query.get(announcement.course_id)

    if not course:
        return jsonify({"message": "Course not found"}), 404

    user = User.query.get(user_id)
    if user.role != UserRole.ADMIN and course.mentor_id != user_id:
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json() or {}
    announcement.title = data.get("title", announcement.title)
    announcement.message = data.get("message", announcement.message)

    db.session.commit()
    return jsonify(announcement.to_dict())


@announcement_bp.route("/<announcement_id>", methods=["DELETE"])
@jwt_required()
@role_required(
    UserRole.MENTOR,
    UserRole.ADMIN,
)
@approved_mentor_required
def delete_announcement(announcement_id):
    user_id = get_jwt_identity()
    announcement = Announcement.query.get_or_404(announcement_id)
    course = Course.query.get(announcement.course_id)

    if not course:
        return jsonify({"message": "Course not found"}), 404

    user = User.query.get(user_id)
    if user.role != UserRole.ADMIN and course.mentor_id != user_id:
        return jsonify({"message": "Access denied"}), 403

    db.session.delete(announcement)
    db.session.commit()
    return jsonify({"message": "Announcement deleted"})


@announcement_bp.route("/<course_id>")
def get_announcements(course_id):

    announcements = Announcement.query.filter_by(
        course_id=course_id
    ).all()

    return jsonify([
        announcement.to_dict()
        for announcement in announcements
    ])
    