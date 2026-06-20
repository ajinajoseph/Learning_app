from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from app.extensions import db

from app.models.course import Course
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.models.user import User

from app.middleware.role_required import role_required


course_bp = Blueprint(
    "course",
    __name__,
    url_prefix="/api/courses"
)


@course_bp.route("", methods=["POST"])
@jwt_required()
@role_required("mentor")
def create_course():

    data = request.get_json()

    user_id = get_jwt_identity()

    course = Course(
        title=data["title"],
        description=data["description"],
        price=data["price"],
        mentor_id=user_id
    )

    db.session.add(course)
    db.session.commit()

    return jsonify(
        course.to_dict()
    ), 201


@course_bp.route("", methods=["GET"])
def get_courses():

    courses = Course.query.all()

    return jsonify([
        course.to_dict()
        for course in courses
    ])


@course_bp.route("/<course_id>", methods=["GET"])
def get_course(course_id):

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    return jsonify(
        course.to_dict()
    )


@course_bp.route("/my-courses")
@jwt_required()
@role_required("mentor")
def my_courses():

    user_id = get_jwt_identity()

    courses = Course.query.filter_by(
        mentor_id=user_id
    ).all()

    return jsonify([
        course.to_dict()
        for course in courses
    ])


@course_bp.route("/search")
def search_courses():

    keyword = request.args.get(
        "q",
        ""
    )

    courses = Course.query.filter(
        Course.title.ilike(
            f"%{keyword}%"
        )
    ).all()

    return jsonify([
        course.to_dict()
        for course in courses
    ])


@course_bp.route("/paginated")
def paginated_courses():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = request.args.get(
        "per_page",
        5,
        type=int
    )

    result = Course.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "courses": [
            course.to_dict()
            for course in result.items
        ],
        "total": result.total,
        "pages": result.pages,
        "current_page": page
    })


@course_bp.route("/<course_id>/content")
@jwt_required()
def course_content(course_id):

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    # Admin can access
    if user.role.value == "admin":
        pass

    # Course owner mentor can access
    elif (
        user.role.value == "mentor"
        and course.mentor_id == user_id
    ):
        pass

    # Enrolled students can access
    elif user.role.value == "student":

        enrollment = Enrollment.query.filter_by(
            student_id=user_id,
            course_id=course_id
        ).first()

        if not enrollment:
            return jsonify({
                "message": "Enroll in the course first"
            }), 403

    else:
        return jsonify({
            "message": "Access denied"
        }), 403

    modules = Module.query.filter_by(
        course_id=course_id
    ).all()

    module_data = []

    for module in modules:

        lessons = Lesson.query.filter_by(
            module_id=module.id
        ).all()

        module_data.append({
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "lessons": [
                lesson.to_dict()
                for lesson in lessons
            ]
        })

    return jsonify({
        "course": course.to_dict(),
        "modules": module_data
    })
@course_bp.route("/<course_id>", methods=["PUT"])
@jwt_required()
def update_course(course_id):

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    if (
        user.role.value != "admin"
        and course.mentor_id != user_id
    ):
        return jsonify({
            "message": "Access denied"
        }), 403

    data = request.get_json()

    course.title = data.get(
        "title",
        course.title
    )

    course.description = data.get(
        "description",
        course.description
    )

    course.price = data.get(
        "price",
        course.price
    )

    db.session.commit()

    return jsonify({
        "message": "Course updated",
        "course": course.to_dict()
    })

@course_bp.route("/<course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    if (
        user.role.value != "admin"
        and course.mentor_id != user_id
    ):
        return jsonify({
            "message": "Access denied"
        }), 403

    db.session.delete(course)

    db.session.commit()

    return jsonify({
        "message": "Course deleted successfully"
    })