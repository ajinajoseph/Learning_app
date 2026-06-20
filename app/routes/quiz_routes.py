from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from app.middleware.role_required import role_required
from app.extensions import db
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.option import Option
from app.models.quiz_attempt import QuizAttempt
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.course import Course
from app.models.user import User
from app.models.user import UserRole
from app.services.notification_service import create_notification
quiz_bp = Blueprint(
    "quiz",
    __name__,
    url_prefix="/api/quizzes"
)

def verify_quiz_owner(quiz_id, user_id):

    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        return None, (
            jsonify({"message": "Quiz not found"}),
            404
        )

    lesson = Lesson.query.get(quiz.lesson_id)

    if not lesson:
        return None, (
            jsonify({"message": "Lesson not found"}),
            404
        )

    module = Module.query.get(lesson.module_id)

    course = Course.query.get(module.course_id)

    user = User.query.get(user_id)

    if user.role != UserRole.ADMIN:

        if course.mentor_id != user_id:
            return None, (
                jsonify({
                    "message": "You do not own this course"
                }),
                403
            )

    return quiz, None

@quiz_bp.route("", methods=["POST"])
@jwt_required()
@role_required("mentor", "admin")
def create_quiz():

    user_id = get_jwt_identity()

    data = request.get_json()

    lesson = Lesson.query.get(
        data["lesson_id"]
    )

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

    user = User.query.get(user_id)

    if user.role != UserRole.ADMIN:

        if course.mentor_id != user_id:
            return jsonify({
                "message": "You do not own this course"
            }), 403

    quiz = Quiz(
        title=data["title"],
        lesson_id=data["lesson_id"]
    )

    db.session.add(quiz)
    db.session.commit()

    return jsonify(
        quiz.to_dict()
    ), 201



@quiz_bp.route("/question", methods=["POST"])
@jwt_required()
@role_required("mentor","admin")
def add_question():

    user_id = get_jwt_identity()

    data = request.get_json()

    quiz, error = verify_quiz_owner(
        data["quiz_id"],
        user_id
    )

    if error:
        return error

    question = Question(
        quiz_id=data["quiz_id"],
        question_text=data["question_text"]
    )

    db.session.add(question)
    db.session.commit()

    return jsonify(
        question.to_dict()
    ), 201

@quiz_bp.route("/option", methods=["POST"])
@jwt_required()
@role_required("mentor","admin")
def add_option():

    user_id = get_jwt_identity()

    data = request.get_json()

    question = Question.query.get(
        data["question_id"]
    )

    if not question:
        return jsonify({
            "message": "Question not found"
        }), 404

    quiz, error = verify_quiz_owner(
        question.quiz_id,
        user_id
    )

    if error:
        return error

    option = Option(
        question_id=data["question_id"],
        option_text=data["option_text"],
        is_correct=data["is_correct"]
    )

    db.session.add(option)
    db.session.commit()

    return jsonify({
        "message": "Option added"
    }), 201

@quiz_bp.route("/<quiz_id>", methods=["PUT"])
@jwt_required()
@role_required("mentor","admin")
def update_quiz(quiz_id):

    user_id = get_jwt_identity()

    quiz, error = verify_quiz_owner(
        quiz_id,
        user_id
    )

    if error:
        return error

    data = request.get_json()

    quiz.title = data.get(
        "title",
        quiz.title
    )

    db.session.commit()

    return jsonify(
        quiz.to_dict()
    )

@quiz_bp.route("/<quiz_id>")
def get_quiz(quiz_id):

    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        return jsonify({
            "message": "Quiz not found"
        }), 404

    questions = Question.query.filter_by(
        quiz_id=quiz_id
    ).all()

    result = []

    for question in questions:

        options = Option.query.filter_by(
            question_id=question.id
        ).all()

        result.append({
            "id": question.id,
            "question": question.question_text,
            "options": [
                option.to_dict()
                for option in options
            ]
        })

    return jsonify({
        "quiz": quiz.to_dict(),
        "questions": result
    })
@quiz_bp.route("/submit/<quiz_id>", methods=["POST"])
@jwt_required()
@role_required("student")
def submit_quiz(quiz_id):

    user_id = get_jwt_identity()

    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        return jsonify({
            "message": "Quiz not found"
        }), 404

    existing_attempt = QuizAttempt.query.filter_by(
        student_id=user_id,
        quiz_id=quiz_id
    ).first()

    if existing_attempt:
        return jsonify({
            "message": "Quiz already submitted"
        }), 400

    data = request.get_json()

    answers = data["answers"]

    score = 0

    for answer in answers:

        option = Option.query.get(
            answer["option_id"]
        )

        if option and option.is_correct:
            score += 1

    attempt = QuizAttempt(
        student_id=user_id,
        quiz_id=quiz_id,
        score=score
    )

    db.session.add(attempt)

    db.session.commit()
    create_notification(
    user_id,
    "Quiz Completed",
    f"You scored {score}"
    )

    return jsonify({
        "score": score
    })

@quiz_bp.route("/<quiz_id>", methods=["DELETE"])
@jwt_required()
@role_required("mentor","admin")
def delete_quiz(quiz_id):

    user_id = get_jwt_identity()

    quiz, error = verify_quiz_owner(
        quiz_id,
        user_id
    )

    if error:
        return error

    db.session.delete(quiz)

    db.session.commit()

    return jsonify({
        "message": "Quiz deleted"
    })

@quiz_bp.route("/my-attempts")
@jwt_required()
@role_required("student")
def my_attempts():

    user_id = get_jwt_identity()

    attempts = QuizAttempt.query.filter_by(
        student_id=user_id
    ).all()

    return jsonify([
        attempt.to_dict()
        for attempt in attempts
    ])