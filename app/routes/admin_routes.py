from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.certificate import Certificate
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.review import Review, ReviewStatus
from app.models.review_report import ReportStatus, ReviewReport
from app.models.enrollment import Enrollment
from app.middleware.role_required import role_required
from app.services.notification_service import create_notification
from app.services.email_service import send_email
from app.services.review_service import get_course_rating_stats
from app.services.elasticsearch_service import delete_course_from_index, index_course
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.option import Option
from app.models.lesson_attachment import LessonAttachment
from app.models.question_thread import QuestionThread
from app.models.notification import Notification
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.models.progress import Progress
from app.models.payment import Payment
from app.models.announcement import Announcement
from app.models.qa_message import QAMessage

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# ─────────────────────────────────────────
# USERS
# ─────────────────────────────────────────

@admin_bp.route("/users")
@jwt_required()
@role_required(UserRole.ADMIN)
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@admin_bp.route("/users/<user_id>/role", methods=["PUT"])
@jwt_required()
@role_required(UserRole.ADMIN)
def change_role(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    role = data.get("role")
    valid_roles = [
        UserRole.STUDENT.value,
        UserRole.MENTOR.value,
        UserRole.ADMIN.value
    ]

    if role not in valid_roles:
        return jsonify({"message": "Invalid role"}), 400

    user.role = UserRole(role)
    if user.role == UserRole.MENTOR:
        user.is_approved = False
    else:
        user.is_approved = True

    db.session.commit()
    return jsonify({"message": "Role updated", "role": user.role.value})


@admin_bp.route("/users/<user_id>", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.ADMIN)
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.role == UserRole.ADMIN:
        return jsonify({"message": "Admin accounts cannot be deleted."}), 403

    try:
        # ── Student related data ──────────────────────────────
        ReviewReport.query.filter_by(
            reporter_id=user.id
        ).delete(synchronize_session=False)

        Review.query.filter_by(
            student_id=user.id
        ).delete(synchronize_session=False)

        Enrollment.query.filter_by(
            student_id=user.id
        ).delete(synchronize_session=False)

        Certificate.query.filter_by(
            student_id=user.id
        ).delete(synchronize_session=False)

        Notification.query.filter_by(
            user_id=user.id
        ).delete(synchronize_session=False)

        Payment.query.filter_by(
            student_id=user.id
        ).delete(synchronize_session=False)

        Progress.query.filter_by(
            student_id=user.id
        ).delete(synchronize_session=False)

        QuizAttempt.query.filter_by(
            student_id=user.id
        ).delete(synchronize_session=False)

        thread_ids = [
    t.id
    for t in QuestionThread.query.filter_by(
        student_id=user.id
    ).all()
]

        if thread_ids:
            Answer.query.filter(
                Answer.question_id.in_(thread_ids)
            ).delete(synchronize_session=False)

        QuestionThread.query.filter_by(
            student_id=user.id
        ).delete(synchronize_session=False)

        QAMessage.query.filter_by(
            user_id=user.id
        ).delete(synchronize_session=False)

        # ── Mentor related data ───────────────────────────────
        if user.role == UserRole.MENTOR:
            Answer.query.filter_by(
                mentor_id=user.id
            ).delete(synchronize_session=False)

            courses = Course.query.filter_by(mentor_id=user.id).all()

            for course in courses:
                # Delete answers by this mentor
                thread_ids = [
                    t.id
                    for t in QuestionThread.query.filter_by(
                        course_id=course.id
                    ).all()
                ]

                if thread_ids:
                    Answer.query.filter(
                        Answer.question_id.in_(thread_ids)
                    ).delete(synchronize_session=False)

                QuestionThread.query.filter_by(
                    course_id=course.id
                ).delete(synchronize_session=False)
                # Delete QA messages and threads for this course
                QAMessage.query.filter_by(
                    course_id=course.id
                ).delete(synchronize_session=False)


                # Delete reviews and their reports
                review_ids = [
                    r.id for r in Review.query.filter_by(
                        course_id=course.id
                    ).all()
                ]
                if review_ids:
                    ReviewReport.query.filter(
                        ReviewReport.review_id.in_(review_ids)
                    ).delete(synchronize_session=False)

                Review.query.filter_by(
                    course_id=course.id
                ).delete(synchronize_session=False)

                # Delete payments and enrollments
                Payment.query.filter_by(
                    course_id=course.id
                ).delete(synchronize_session=False)

                Enrollment.query.filter_by(
                    course_id=course.id
                ).delete(synchronize_session=False)

                # Delete announcements
                Announcement.query.filter_by(
                    course_id=course.id
                ).delete(synchronize_session=False)

                # Delete certificates
                Certificate.query.filter_by(
                    course_id=course.id
                ).delete(synchronize_session=False)

                # Delete modules → lessons → attachments,
                # progress, quizzes → questions → options
                modules = Module.query.filter_by(
                    course_id=course.id
                ).all()

                for module in modules:
                    lessons = Lesson.query.filter_by(
                        module_id=module.id
                    ).all()

                    for lesson in lessons:
                        # Attachments
                        LessonAttachment.query.filter_by(
                            lesson_id=lesson.id
                        ).delete(synchronize_session=False)

                        # Progress
                        Progress.query.filter_by(
                            lesson_id=lesson.id
                        ).delete(synchronize_session=False)

                        # Quizzes
                        quizzes = Quiz.query.filter_by(
                            lesson_id=lesson.id
                        ).all()

                        for quiz in quizzes:
                            QuizAttempt.query.filter_by(
                                quiz_id=quiz.id
                            ).delete(synchronize_session=False)

                            questions = Question.query.filter_by(
                                quiz_id=quiz.id
                            ).all()

                            for question in questions:
                                Option.query.filter_by(
                                    question_id=question.id
                                ).delete(synchronize_session=False)
                                db.session.delete(question)

                            db.session.delete(quiz)

                        db.session.delete(lesson)

                    db.session.delete(module)

                # Delete elasticsearch index
                try:
                    delete_course_from_index(course.id)
                except Exception:
                    pass

                db.session.delete(course)

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        print("DELETE USER ERROR:", traceback.format_exc())
        return jsonify({"message": str(e)}), 500


# ─────────────────────────────────────────
# COURSES
# ─────────────────────────────────────────

@admin_bp.route("/courses")
@jwt_required()
@role_required(UserRole.ADMIN)
def get_all_courses():
    courses = Course.query.all()
    return jsonify([course.to_dict() for course in courses])


@admin_bp.route("/courses/<course_id>/approve", methods=["PUT"])
@jwt_required()
@role_required(UserRole.ADMIN)
def approve_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 404

    course.is_approved = True
    db.session.commit()
    index_course(course)

    create_notification(
        course.mentor_id,
        "Course Approved",
        f"Your course '{course.title}' has been approved."
    )
    send_email(
        course.mentor.email,
        "Course Approved",
        f"Your course '{course.title}' has been approved."
    )

    return jsonify({"message": "Course approved successfully"})


@admin_bp.route("/courses/<course_id>/reject", methods=["PUT"])
@jwt_required()
@role_required(UserRole.ADMIN)
def reject_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 404

    course.is_approved = False
    db.session.commit()
    delete_course_from_index(course_id)

    create_notification(
        course.mentor_id,
        "Course Rejected",
        f"Your course '{course.title}' was rejected and is no longer published."
    )
    send_email(
        course.mentor.email,
        "Course Rejected",
        f"Your course '{course.title}' was rejected and is no longer published."
    )

    return jsonify({"message": "Course rejected successfully"})


@admin_bp.route("/courses/<course_id>", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.ADMIN)
def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 404

    try:
        # Use the same thorough cascade delete as course_routes.py
        modules = Module.query.filter_by(course_id=course.id).all()
        module_ids = [m.id for m in modules]
        lessons = Lesson.query.filter(
            Lesson.module_id.in_(module_ids)
        ).all() if module_ids else []
        lesson_ids = [l.id for l in lessons]
        quizzes = Quiz.query.filter(
            Quiz.lesson_id.in_(lesson_ids)
        ).all() if lesson_ids else []
        quiz_ids = [q.id for q in quizzes]
        questions = Question.query.filter(
            Question.quiz_id.in_(quiz_ids)
        ).all() if quiz_ids else []
        question_ids = [q.id for q in questions]

        Progress.query.filter(
            Progress.lesson_id.in_(lesson_ids)
        ).delete(synchronize_session=False)

        LessonAttachment.query.filter(
            LessonAttachment.lesson_id.in_(lesson_ids)
        ).delete(synchronize_session=False)

        QuizAttempt.query.filter(
            QuizAttempt.quiz_id.in_(quiz_ids)
        ).delete(synchronize_session=False)

        Option.query.filter(
            Option.question_id.in_(question_ids)
        ).delete(synchronize_session=False)

        Question.query.filter(
            Question.quiz_id.in_(quiz_ids)
        ).delete(synchronize_session=False)

        Quiz.query.filter(
            Quiz.lesson_id.in_(lesson_ids)
        ).delete(synchronize_session=False)

        thread_ids = [
            t.id for t in QuestionThread.query.filter_by(
                course_id=course_id
            ).all()
        ]
        if thread_ids:
            Answer.query.filter(
                Answer.question_id.in_(thread_ids)
            ).delete(synchronize_session=False)

        QuestionThread.query.filter_by(
            course_id=course_id
        ).delete(synchronize_session=False)

        QAMessage.query.filter_by(
            course_id=course_id
        ).delete(synchronize_session=False)

        Announcement.query.filter_by(
            course_id=course_id
        ).delete(synchronize_session=False)

        review_ids = [
            r.id for r in Review.query.filter_by(
                course_id=course_id
            ).all()
        ]
        if review_ids:
            ReviewReport.query.filter(
                ReviewReport.review_id.in_(review_ids)
            ).delete(synchronize_session=False)

        Review.query.filter_by(
            course_id=course_id
        ).delete(synchronize_session=False)

        Enrollment.query.filter_by(
            course_id=course_id
        ).delete(synchronize_session=False)

        Payment.query.filter_by(
            course_id=course_id
        ).delete(synchronize_session=False)

        Certificate.query.filter_by(
            course_id=course_id
        ).delete(synchronize_session=False)

        for lesson in lessons:
            db.session.delete(lesson)
        for module in modules:
            db.session.delete(module)

        db.session.delete(course)
        db.session.commit()

        try:
            delete_course_from_index(course_id)
        except Exception:
            pass

        return jsonify({"message": "Course deleted successfully"})

    except Exception as e:
        db.session.rollback()
        import traceback
        print("ADMIN DELETE COURSE ERROR:", traceback.format_exc())
        return jsonify({"message": str(e)}), 500


# ─────────────────────────────────────────
# MENTORS
# ─────────────────────────────────────────

@admin_bp.route("/mentors/pending")
@jwt_required()
@role_required(UserRole.ADMIN)
def pending_mentors():
    mentors = User.query.filter_by(
        role=UserRole.MENTOR,
        is_approved=False,
    ).all()
    return jsonify([user.to_dict() for user in mentors])


@admin_bp.route("/mentors/<user_id>/approve", methods=["PUT"])
@jwt_required()
@role_required(UserRole.ADMIN)
def approve_mentor(user_id):
    user = User.query.get(user_id)
    if not user or user.role != UserRole.MENTOR:
        return jsonify({"message": "Mentor not found"}), 404

    user.is_approved = True
    db.session.commit()

    create_notification(
        user.id,
        "Mentor Approved",
        "Your mentor account has been approved."
    )
    send_email(
        user.email,
        "Mentor Approved",
        "Your mentor account has been approved. You can now create courses."
    )

    return jsonify({
        "message": "Mentor approved successfully",
        "user": user.to_dict()
    })


@admin_bp.route("/mentors/<user_id>/reject", methods=["PUT"])
@jwt_required()
@role_required(UserRole.ADMIN)
def reject_mentor(user_id):
    user = User.query.get(user_id)
    if not user or user.role != UserRole.MENTOR:
        return jsonify({"message": "Mentor not found"}), 404

    user.is_approved = False
    db.session.commit()

    create_notification(
        user.id,
        "Mentor Application Rejected",
        "Your mentor account application was not approved."
    )
    send_email(
        user.email,
        "Mentor Application Rejected",
        "Your mentor account application was not approved."
    )

    return jsonify({
        "message": "Mentor rejected successfully",
        "user": user.to_dict()
    })


# ─────────────────────────────────────────
# REVIEWS
# ─────────────────────────────────────────

@admin_bp.route("/reviews/<review_id>", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.ADMIN)
def delete_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404

    ReviewReport.query.filter_by(review_id=review_id).delete()
    course_id = review.course_id
    db.session.delete(review)
    db.session.commit()

    course = Course.query.get(course_id)
    if course:
        index_course(course)

    return jsonify({"message": "Review deleted"})


@admin_bp.route("/reviews/<review_id>/moderate", methods=["PUT"])
@jwt_required()
@role_required(UserRole.ADMIN)
def admin_moderate_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404

    data = request.get_json() or {}
    action = data.get("action")

    if action == "approve":
        review.status = ReviewStatus.APPROVED
    elif action == "reject":
        review.status = ReviewStatus.REJECTED
    else:
        return jsonify({
            "message": "action must be 'approve' or 'reject'"
        }), 400

    db.session.commit()

    course = Course.query.get(review.course_id)
    if course:
        index_course(course)

    return jsonify({
        "message": f"Review {action}d",
        "review": review.to_dict(),
        "rating_stats": get_course_rating_stats(review.course_id),
    })


# ─────────────────────────────────────────
# REVIEW REPORTS
# ─────────────────────────────────────────

@admin_bp.route("/review-reports", methods=["GET"])
@jwt_required()
@role_required(UserRole.ADMIN)
def get_review_reports():
    reports = ReviewReport.query.filter_by(
        status=ReportStatus.PENDING
    ).all()
    return jsonify([report.to_dict() for report in reports])


@admin_bp.route("/review-reports/<report_id>", methods=["PUT"])
@jwt_required()
@role_required(UserRole.ADMIN)
def resolve_review_report(report_id):
    report = ReviewReport.query.get(report_id)
    if not report:
        return jsonify({"message": "Report not found"}), 404

    data = request.get_json() or {}
    action = data.get("action")

    if action == "resolve":
        report.status = ReportStatus.RESOLVED
        review = Review.query.get(report.review_id)
        if review:
            review.status = ReviewStatus.REJECTED
    elif action == "dismiss":
        report.status = ReportStatus.DISMISSED
    else:
        return jsonify({
            "message": "action must be 'resolve' or 'dismiss'"
        }), 400

    db.session.commit()

    review = Review.query.get(report.review_id)
    if review:
        course = Course.query.get(review.course_id)
        if course:
            index_course(course)

    return jsonify({
        "message": f"Report {action}d",
        "report": report.to_dict()
    })


# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────

@admin_bp.route("/dashboard")
@jwt_required()
@role_required(UserRole.ADMIN)
def dashboard():
    total_users = User.query.count()
    total_students = User.query.filter_by(role=UserRole.STUDENT).count()
    total_mentors = User.query.filter_by(role=UserRole.MENTOR).count()
    total_courses = Course.query.count()
    approved_courses = Course.query.filter_by(is_approved=True).count()
    pending_mentors = User.query.filter_by(
        role=UserRole.MENTOR,
        is_approved=False
    ).count()
    total_reviews = Review.query.count()
    total_enrollments = Enrollment.query.count()

    return jsonify({
        "total_users": total_users,
        "total_students": total_students,
        "total_mentors": total_mentors,
        "total_courses": total_courses,
        "approved_courses": approved_courses,
        "pending_mentors": pending_mentors,
        "total_reviews": total_reviews,
        "total_enrollments": total_enrollments
    })