import math

from app.models.question import Question
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt


def required_quiz_score(quiz):
    total_questions = Question.query.filter_by(quiz_id=quiz.id).count()
    if total_questions == 0:
        return 0
    return math.ceil(total_questions * quiz.pass_percentage / 100)


def has_passed_quiz(student_id, quiz):
    total_questions = Question.query.filter_by(quiz_id=quiz.id).count()
    if total_questions == 0:
        return True

    attempt = QuizAttempt.query.filter_by(
        student_id=student_id,
        quiz_id=quiz.id,
    ).first()
    if not attempt:
        return False

    return attempt.score >= required_quiz_score(quiz)


def quiz_summary_for_student(student_id, quiz):
    data = quiz.to_dict()
    attempt = QuizAttempt.query.filter_by(
        student_id=student_id,
        quiz_id=quiz.id,
    ).first()
    if attempt:
        data["attempt"] = attempt.to_dict()
    data["passed"] = has_passed_quiz(student_id, quiz)
    data["required_score"] = required_quiz_score(quiz)
    return data
