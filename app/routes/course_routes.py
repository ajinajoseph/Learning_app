from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.middleware.role_required import role_required
from app.middleware.mentor_approved import approved_mentor_required
from app.models.course import Course, CourseLevel
from app.models.user import User, UserRole
from app.services.course_access import user_has_course_access
from app.services.curriculum_service import build_course_content
from app.services.elasticsearch_service import (
    delete_course_from_index,
    index_course,
    search_courses,
)


course_bp = Blueprint(
    "course",
    __name__,
    url_prefix="/api/courses",
)


def _parse_level(value):
    if not value:
        return CourseLevel.BEGINNER
    return CourseLevel(value.lower())


@course_bp.route("", methods=["POST"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def create_course():
    data = request.get_json() or {}
    user_id = get_jwt_identity()

    try:
        level = _parse_level(data.get("level"))
    except ValueError:
        return jsonify({"message": "Invalid course level"}), 400

    course = Course(
        title=data["title"],
        description=data["description"],
        price=data["price"],
        level=level,
        duration_hours=float(data.get("duration_hours", 0)),
        language=data.get("language", "english"),
        tags=data.get("tags") or [],
        mentor_id=user_id,
    )

    db.session.add(course)
    db.session.commit()
    index_course(course)

    return jsonify(course.to_dict()), 201


@course_bp.route("", methods=["GET"])
def get_courses():
    courses = Course.query.filter_by(is_approved=True).all()
    return jsonify([course.to_dict() for course in courses]), 200


@course_bp.route("/<course_id>", methods=["GET"])
def get_course(course_id):
    course = Course.query.get(course_id)

    if not course:
        return jsonify({"message": "Course not found"}), 404

    return jsonify(course.to_dict()), 200


@course_bp.route("/my-courses")
@jwt_required()
@role_required(UserRole.MENTOR)
def my_courses():
    user_id = get_jwt_identity()
    courses = Course.query.filter_by(mentor_id=user_id).all()
    return jsonify([course.to_dict() for course in courses]), 200


@course_bp.route("/search")
def search_courses_legacy():
    params = {
        "q": request.args.get("q", ""),
        "min_price": request.args.get("min_price", type=float),
        "max_price": request.args.get("max_price", type=float),
        "level": request.args.get("level"),
        "min_duration": request.args.get("min_duration", type=float),
        "max_duration": request.args.get("max_duration", type=float),
        "language": request.args.get("language"),
        "min_rating": request.args.get("min_rating", type=float),
        "tags": request.args.get("tags"),
        "page": request.args.get("page", 1, type=int),
        "per_page": request.args.get("per_page", 10, type=int),
    }
    return jsonify(search_courses(params)), 200


@course_bp.route("/paginated")
def paginated_courses():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    result = Course.query.filter_by(is_approved=True).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return jsonify({
        "courses": [course.to_dict() for course in result.items],
        "total": result.total,
        "pages": result.pages,
        "current_page": page,
    }), 200


@course_bp.route("/<course_id>/content")
@jwt_required()
def course_content(course_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    course = Course.query.get(course_id)

    if not course:
        return jsonify({"message": "Course not found"}), 404

    if user.role == UserRole.ADMIN:
        pass
    elif user.role == UserRole.MENTOR and course.mentor_id == user_id:
        pass
    elif user.role == UserRole.STUDENT:
        if not user_has_course_access(user_id, course_id):
            return jsonify({"message": "Enroll in the course first"}), 403
    else:
        return jsonify({"message": "Access denied"}), 403

    student_id = user_id if user.role == UserRole.STUDENT else None
    module_data = build_course_content(
        course_id,
        presign_media=True,
        student_id=student_id,
    )

    return jsonify({
        "course": course.to_dict(),
        "modules": module_data,
    }), 200


@course_bp.route("/<course_id>", methods=["PUT"])
@jwt_required()
def update_course(course_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    course = Course.query.get(course_id)

    if not course:
        return jsonify({"message": "Course not found"}), 404

    if user.role != UserRole.ADMIN and course.mentor_id != user_id:
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json() or {}

    course.title = data.get("title", course.title)
    course.description = data.get("description", course.description)
    course.price = data.get("price", course.price)
    course.duration_hours = float(
        data.get("duration_hours", course.duration_hours)
    )
    course.language = data.get("language", course.language)
    course.tags = data.get("tags", course.tags or [])

    if "level" in data:
        try:
            course.level = _parse_level(data.get("level"))
        except ValueError:
            return jsonify({"message": "Invalid course level"}), 400

    db.session.commit()
    index_course(course)

    return jsonify({
        "message": "Course updated",
        "course": course.to_dict(),
    }), 200


@course_bp.route("/<course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        course = Course.query.get(course_id)

        if not course:
            return jsonify({"message": "Course not found"}), 404

        if user.role != UserRole.ADMIN and str(course.mentor_id) != str(user_id):
            return jsonify({"message": "Access denied"}), 403

        from app.models.announcement import Announcement
        from app.models.answer import Answer
        from app.models.enrollment import Enrollment
        from app.models.lesson import Lesson
        from app.models.lesson_attachment import LessonAttachment
        from app.models.module import Module
        from app.models.option import Option
        from app.models.payment import Payment
        from app.models.progress import Progress
        from app.models.qa_message import QAMessage
        from app.models.question import Question
        from app.models.question_thread import QuestionThread
        from app.models.quiz import Quiz
        from app.models.quiz_attempt import QuizAttempt
        from app.models.review import Review
        from app.models.review_report import ReviewReport

        modules = Module.query.filter_by(course_id=course.id).all()
        module_ids = [module.id for module in modules]
        lessons = Lesson.query.filter(Lesson.module_id.in_(module_ids)).all() if module_ids else []
        lesson_ids = [lesson.id for lesson in lessons]
        quizzes = Quiz.query.filter(Quiz.lesson_id.in_(lesson_ids)).all() if lesson_ids else []
        quiz_ids = [quiz.id for quiz in quizzes]
        questions = Question.query.filter(Question.quiz_id.in_(quiz_ids)).all() if quiz_ids else []
        question_ids = [question.id for question in questions]

        Progress.query.filter(Progress.lesson_id.in_(lesson_ids)).delete(synchronize_session=False)
        LessonAttachment.query.filter(LessonAttachment.lesson_id.in_(lesson_ids)).delete(synchronize_session=False)
        QuizAttempt.query.filter(QuizAttempt.quiz_id.in_(quiz_ids)).delete(synchronize_session=False)
        Option.query.filter(Option.question_id.in_(question_ids)).delete(synchronize_session=False)
        Question.query.filter(Question.quiz_id.in_(quiz_ids)).delete(synchronize_session=False)
        Quiz.query.filter(Quiz.lesson_id.in_(lesson_ids)).delete(synchronize_session=False)

        Answer.query.filter(Answer.question_id.in_([thread.id for thread in QuestionThread.query.filter_by(course_id=course_id).all()])).delete(synchronize_session=False)
        QuestionThread.query.filter_by(course_id=course_id).delete(synchronize_session=False)
        QAMessage.query.filter_by(course_id=course_id).delete(synchronize_session=False)
        Announcement.query.filter_by(course_id=course_id).delete(synchronize_session=False)

        reviews = Review.query.filter_by(course_id=course_id).all()
        review_ids = [review.id for review in reviews]
        ReviewReport.query.filter(ReviewReport.review_id.in_(review_ids)).delete(synchronize_session=False)
        Review.query.filter_by(course_id=course_id).delete(synchronize_session=False)

        Enrollment.query.filter_by(course_id=course_id).delete(synchronize_session=False)
        Payment.query.filter_by(course_id=course_id).delete(synchronize_session=False)

        for lesson in lessons:
            db.session.delete(lesson)
        for module in modules:
            db.session.delete(module)

        db.session.delete(course)
        db.session.commit()

        try:
            delete_course_from_index(course_id)
        except Exception:
            pass # Ignore Elasticsearch deletion errors if not running

        return jsonify({"message": "Course deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        print("DELETE COURSE ERROR:", traceback.format_exc())
        return jsonify({"message": str(e)}), 500


@course_bp.route("/<course_id>/students", methods=["GET"])
@jwt_required()
def get_enrolled_students(course_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    course = Course.query.get_or_404(course_id)

    # Verify ownership
    if user.role != UserRole.ADMIN and str(course.mentor_id) != str(user_id):
        return jsonify({"message": "Unauthorized"}), 403

    from app.models.enrollment import Enrollment
    from app.models.module import Module
    from app.models.lesson import Lesson
    from app.models.progress import Progress

    enrollments = Enrollment.query.filter_by(course_id=course_id).all()

    # Get total lessons in the course to calculate progress percentage
    modules = Module.query.filter_by(course_id=course_id).all()
    module_ids = [m.id for m in modules]
    lessons = Lesson.query.filter(Lesson.module_id.in_(module_ids)).all() if module_ids else []
    total_lessons = len(lessons)
    lesson_ids = [l.id for l in lessons]

    students_data = []
    for enrollment in enrollments:
        student = User.query.get(enrollment.student_id)
        if not student:
            continue

        # Calculate progress percentage
        completed_lessons_count = 0
        if total_lessons > 0 and lesson_ids:
            completed_lessons_count = Progress.query.filter(
                Progress.student_id == student.id,
                Progress.lesson_id.in_(lesson_ids),
                Progress.completed == True
            ).count()

        progress_percentage = 0
        if total_lessons > 0:
            progress_percentage = round((completed_lessons_count / total_lessons) * 100, 2)

        students_data.append({
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "progress_percentage": progress_percentage,
            "enrolled_at": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None
        })

    return jsonify(students_data), 200
