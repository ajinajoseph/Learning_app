from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from app.middleware.role_required import role_required
from app.middleware.mentor_approved import approved_mentor_required
from app.extensions import db
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.option import Option
from app.models.quiz_attempt import QuizAttempt
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.course import Course
from app.models.user import User, UserRole
from app.services.course_access import (
    get_course_id_for_quiz,
    user_has_course_access,
)
from app.services.notification_service import create_notification
from app.services.quiz_service import has_passed_quiz, required_quiz_score

quiz_bp = Blueprint(
    "quiz",
    __name__,
    url_prefix="/api/quizzes"
)

# ─────────────────────────────────────────
# Handle ALL OPTIONS preflight for this blueprint
# before JWT or role decorators can block it
# ─────────────────────────────────────────
@quiz_bp.before_request
def handle_options():
    if request.method == "OPTIONS":
        response = jsonify({"message": "OK"})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response, 200


# ─────────────────────────────────────────
# Helper
# ─────────────────────────────────────────
def verify_quiz_owner(quiz_id, user_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return None, (jsonify({"message": "Quiz not found"}), 404)

    lesson = Lesson.query.get(quiz.lesson_id)
    if not lesson:
        return None, (jsonify({"message": "Lesson not found"}), 404)

    module = Module.query.get(lesson.module_id)
    course = Course.query.get(module.course_id)
    user = User.query.get(user_id)

    if user.role != UserRole.ADMIN:
        if course.mentor_id != user_id:
            return None, (jsonify({"message": "You do not own this course"}), 403)

    return quiz, None


# ─────────────────────────────────────────
# CREATE QUIZ
# ─────────────────────────────────────────
@quiz_bp.route("", methods=["POST"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def create_quiz():
    user_id = get_jwt_identity()
    data = request.get_json()

    lesson = Lesson.query.get(data["lesson_id"])
    if not lesson:
        return jsonify({"message": "Lesson not found"}), 404

    module = Module.query.get(lesson.module_id)
    course = Course.query.get(module.course_id)
    user = User.query.get(user_id)

    if user.role != UserRole.ADMIN:
        if course.mentor_id != user_id:
            return jsonify({"message": "You do not own this course"}), 403

    quiz = Quiz(
        title=data["title"],
        lesson_id=data["lesson_id"],
        pass_percentage=float(data.get("pass_percentage", 70)),
    )
    db.session.add(quiz)
    db.session.commit()

    return jsonify(quiz.to_dict()), 201


# ─────────────────────────────────────────
# GET QUIZ
# ─────────────────────────────────────────
@quiz_bp.route("/<quiz_id>", methods=["GET"])
@jwt_required()
def get_quiz(quiz_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    course_id = get_course_id_for_quiz(quiz_id)

    if not course_id:
        return jsonify({"message": "Quiz not found"}), 404

    if not user_has_course_access(user_id, course_id):
        return jsonify({"message": "Access denied"}), 403

    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    course = Course.query.get(course_id)
    can_view_answers = (
        user.role == UserRole.ADMIN
        or (user.role == UserRole.MENTOR and course.mentor_id == user_id)
    )

    result = []
    for question in questions:
        options = Option.query.filter_by(question_id=question.id).all()
        option_data = []
        for option in options:
            item = {
                "id": option.id,
                "option_text": option.option_text,
            }
            if can_view_answers:
                item["is_correct"] = option.is_correct
            option_data.append(item)

        result.append({
            "id": question.id,
            "question": question.question_text,
            "question_text": question.question_text,
            "options": option_data,
        })

    return jsonify({
        "quiz": quiz.to_dict(),
        "questions": result
    })


# ─────────────────────────────────────────
# UPDATE QUIZ
# ─────────────────────────────────────────
@quiz_bp.route("/<quiz_id>", methods=["PUT"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def update_quiz(quiz_id):
    user_id = get_jwt_identity()
    quiz, error = verify_quiz_owner(quiz_id, user_id)
    if error:
        return error

    data = request.get_json()
    quiz.title = data.get("title", quiz.title)
    if "pass_percentage" in data:
        quiz.pass_percentage = float(data["pass_percentage"])

    db.session.commit()
    return jsonify(quiz.to_dict())


# ─────────────────────────────────────────
# DELETE QUIZ
# ─────────────────────────────────────────
@quiz_bp.route("/<quiz_id>", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def delete_quiz(quiz_id):
    user_id = get_jwt_identity()
    try:
        quiz, error = verify_quiz_owner(quiz_id, user_id)
        if error:
            return error

        question_ids = [
            q.id for q in Question.query.filter_by(quiz_id=quiz.id).all()
        ]
        if question_ids:
            Option.query.filter(
                Option.question_id.in_(question_ids)
            ).delete(synchronize_session=False)

        Question.query.filter_by(quiz_id=quiz.id).delete(synchronize_session=False)
        QuizAttempt.query.filter_by(quiz_id=quiz.id).delete(synchronize_session=False)
        db.session.delete(quiz)
        db.session.commit()

        return jsonify({"message": "Quiz deleted"})
    except Exception as e:
        db.session.rollback()
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": str(e)}), 500


# ─────────────────────────────────────────
# ADD QUESTION
# ─────────────────────────────────────────
@quiz_bp.route("/question", methods=["POST"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def add_question():
    user_id = get_jwt_identity()
    data = request.get_json()

    quiz, error = verify_quiz_owner(data["quiz_id"], user_id)
    if error:
        return error

    question = Question(
        quiz_id=data["quiz_id"],
        question_text=data["question_text"]
    )
    db.session.add(question)
    db.session.commit()

    return jsonify(question.to_dict()), 201


# ─────────────────────────────────────────
# UPDATE QUESTION
# ─────────────────────────────────────────
@quiz_bp.route("/question/<question_id>", methods=["PUT"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def update_question(question_id):
    try:
        data = request.get_json() or {}
        question = Question.query.get_or_404(question_id)
        user_id = get_jwt_identity()

        _, error = verify_quiz_owner(question.quiz_id, user_id)
        if error:
            return error

        # Accept both question_text and text field names
        question_text = data.get('question_text') or data.get('text')
        if question_text:
            question.question_text = question_text

        # Update options if provided
        if 'options' in data:
            for opt_data in data['options']:
                option_id = opt_data.get('id')
                if not option_id:
                    continue
                option = Option.query.get(option_id)
                if option and option.question_id == question.id:
                    option.option_text = (
                        opt_data.get('option_text')
                        or opt_data.get('text')
                        or option.option_text
                    )
                    option.is_correct = opt_data.get('is_correct', option.is_correct)

        db.session.commit()

        options = Option.query.filter_by(question_id=question.id).all()
        return jsonify({
            "message": "Question updated successfully",
            "question": {
                "id": str(question.id),
                "quiz_id": question.quiz_id,
                "question_text": question.question_text,
                "question": question.question_text,
                "options": [
                    {
                        "id": str(o.id),
                        "option_text": o.option_text,
                        "is_correct": o.is_correct
                    } for o in options
                ]
            }
        })
    except Exception as e:
        db.session.rollback()
        import traceback
        print("UPDATE QUESTION ERROR:", traceback.format_exc())
        return jsonify({"message": str(e)}), 500


# ─────────────────────────────────────────
# DELETE QUESTION
# ─────────────────────────────────────────
@quiz_bp.route("/question/<question_id>", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def delete_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        user_id = get_jwt_identity()

        _, error = verify_quiz_owner(question.quiz_id, user_id)
        if error:
            return error

        Option.query.filter_by(question_id=question_id).delete()
        db.session.delete(question)
        db.session.commit()

        return jsonify({"message": "Question deleted"})
    except Exception as e:
        db.session.rollback()
        import traceback
        print("DELETE QUESTION ERROR:", traceback.format_exc())
        return jsonify({"message": str(e)}), 500


# ─────────────────────────────────────────
# ADD OPTION
# ─────────────────────────────────────────
@quiz_bp.route("/option", methods=["POST"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def add_option():
    user_id = get_jwt_identity()
    data = request.get_json()

    question = Question.query.get(data["question_id"])
    if not question:
        return jsonify({"message": "Question not found"}), 404

    quiz, error = verify_quiz_owner(question.quiz_id, user_id)
    if error:
        return error

    option = Option(
        question_id=data["question_id"],
        option_text=data["option_text"],
        is_correct=data["is_correct"]
    )
    db.session.add(option)
    db.session.commit()

    return jsonify({"message": "Option added"}), 201


# ─────────────────────────────────────────
# UPDATE OPTION
# ─────────────────────────────────────────
@quiz_bp.route("/option/<option_id>", methods=["PUT"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def update_option(option_id):
    try:
        data = request.get_json() or {}
        option = Option.query.get_or_404(option_id)
        question = Question.query.get(option.question_id)
        if not question:
            return jsonify({"message": "Question not found"}), 404

        user_id = get_jwt_identity()
        _, error = verify_quiz_owner(question.quiz_id, user_id)
        if error:
            return error

        option.option_text = data.get('option_text', option.option_text)
        option.is_correct = data.get('is_correct', option.is_correct)
        db.session.commit()

        return jsonify({"message": "Option updated"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


# ─────────────────────────────────────────
# DELETE OPTION
# ─────────────────────────────────────────
@quiz_bp.route("/option/<option_id>", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.MENTOR)
@approved_mentor_required
def delete_option(option_id):
    try:
        option = Option.query.get_or_404(option_id)
        question = Question.query.get(option.question_id)
        if not question:
            return jsonify({"message": "Question not found"}), 404

        user_id = get_jwt_identity()
        _, error = verify_quiz_owner(question.quiz_id, user_id)
        if error:
            return error

        db.session.delete(option)
        db.session.commit()

        return jsonify({"message": "Option deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


# ─────────────────────────────────────────
# SUBMIT QUIZ
# ─────────────────────────────────────────
@quiz_bp.route("/submit/<quiz_id>", methods=["POST"])
@jwt_required()
@role_required(UserRole.STUDENT)
def submit_quiz(quiz_id):
    user_id = get_jwt_identity()
    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        return jsonify({"message": "Quiz not found"}), 404

    course_id = get_course_id_for_quiz(quiz_id)
    if not course_id or not user_has_course_access(user_id, course_id):
        return jsonify({"message": "Access denied"}), 403

    existing_attempt = QuizAttempt.query.filter_by(
        student_id=user_id,
        quiz_id=quiz_id
    ).first()
    if existing_attempt:
        return jsonify({"message": "Quiz already submitted"}), 400

    data = request.get_json()
    answers = data["answers"]
    score = 0

    for answer in answers:
        option = Option.query.get(answer["option_id"])
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
        f"You scored {score}",
    )

    return jsonify({
        "score": score,
        "required_score": required_quiz_score(quiz),
        "passed": has_passed_quiz(user_id, quiz),
    })


# ─────────────────────────────────────────
# MY ATTEMPTS
# ─────────────────────────────────────────
@quiz_bp.route("/my-attempts", methods=["GET"])
@jwt_required()
@role_required(UserRole.STUDENT)
def my_attempts():
    user_id = get_jwt_identity()
    attempts = QuizAttempt.query.filter_by(student_id=user_id).all()
    return jsonify([attempt.to_dict() for attempt in attempts])