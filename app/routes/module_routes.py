from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.user import UserRole
from app.middleware.role_required import role_required
from app.models.module import Module
from app.models.course import Course
from app.models.user import User

module_bp = Blueprint(
    "module",
    __name__,
    url_prefix="/api/modules"
)

@module_bp.route("", methods=["POST"])
@jwt_required()
@role_required(UserRole.MENTOR)
def create_module():

    user_id = get_jwt_identity()

    data = request.get_json()

    course = Course.query.get(
        data.get("course_id")
    )

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    if course.mentor_id != user_id:
        return jsonify({
            "message": "Not your course"
        }), 403

    module = Module(
        title=data["title"],
        description=data.get("description"),
        course_id=data["course_id"]
    )

    db.session.add(module)
    db.session.commit()

    return jsonify(
        module.to_dict()
    ), 201


@module_bp.route("/course/<course_id>")
def get_modules(course_id):

    modules = Module.query.filter_by(
        course_id=course_id
    ).all()

    return jsonify([
        module.to_dict()
        for module in modules
    ])

@module_bp.route("/<module_id>", methods=["GET"])
def get_module(module_id):

    module = Module.query.get(module_id)

    if not module:
        return jsonify({
            "message": "Module not found"
        }), 404

    return jsonify(
        module.to_dict()
    )

@module_bp.route("/<module_id>", methods=["PUT"])
@jwt_required()
@role_required(UserRole.MENTOR)
def update_module(module_id):

    user_id = get_jwt_identity()

    module = Module.query.get(module_id)

    if not module:
        return jsonify({
            "message": "Module not found"
        }), 404

    course = Course.query.get(
        module.course_id
    )

    if course.mentor_id != user_id:
        return jsonify({
            "message": "Not your course"
        }), 403

    data = request.get_json()

    module.title = data.get(
        "title",
        module.title
    )

    module.description = data.get(
        "description",
        module.description
    )

    db.session.commit()

    return jsonify(
        module.to_dict()
    )

@module_bp.route("/<module_id>", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.MENTOR)
def delete_module(module_id):

    user_id = get_jwt_identity()

    module = Module.query.get(module_id)

    if not module:
        return jsonify({
            "message": "Module not found"
        }), 404

    course = Course.query.get(
        module.course_id
    )

    if course.mentor_id != user_id:
        return jsonify({
            "message": "Not your course"
        }), 403

    db.session.delete(module)
    db.session.commit()

    return jsonify({
        "message": "Module deleted"
    })