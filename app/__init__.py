from flask import Flask, app

from app.config.config import Config

from app.extensions import db
from app.extensions import migrate
from app.extensions import jwt
from app.models.user import User
from app.models.course import Course
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.models.review import Review
from app.models.progress import Progress
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.option import Option
from app.models.quiz_attempt import QuizAttempt
from app.routes.auth_routes import auth_bp
from app.routes.course_routes import course_bp
from app.routes.module_routes import module_bp
from app.routes.lesson_routes import lesson_bp
from app.routes.enrollement_routes import enrollment_bp
from app.routes.progress_routes import progress_bp
from app.routes.review_routes import review_bp
from app.routes.quiz_routes import quiz_bp
from app.routes.admin_routes import admin_bp
from app.routes.analytics_routes import analytics_bp
from app.routes.notification_routes import notification_bp
from app.routes.certificate_routes import (
    certificate_bp
)
def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    migrate.init_app(app, db)

    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(module_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(enrollment_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(certificate_bp)
    app.register_blueprint(notification_bp)
    return app