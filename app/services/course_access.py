from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.quiz import Quiz
from app.models.user import User, UserRole


def user_has_course_access(user_id, course_id):
    user = User.query.get(user_id)
    if not user:
        return False

    course = Course.query.get(course_id)
    if not course:
        return False

    if user.role == UserRole.ADMIN:
        return True

    if user.role == UserRole.MENTOR and course.mentor_id == user_id:
        return True

    if user.role == UserRole.STUDENT:
        return Enrollment.query.filter_by(
            student_id=user_id,
            course_id=course_id,
        ).first() is not None

    return False


def get_course_id_for_module(module_id):
    module = Module.query.get(module_id)
    return module.course_id if module else None


def get_course_id_for_lesson(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return None
    module = Module.query.get(lesson.module_id)
    return module.course_id if module else None


def get_course_id_for_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return None
    return get_course_id_for_lesson(quiz.lesson_id)
