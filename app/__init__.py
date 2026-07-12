from flask import Flask
import stripe
from app.config.config import Config
from app.extensions import db, migrate, jwt, mail, socketio
from flask_cors import CORS

from app.sockets import qa_sockets
from app.sockets import notification_socket
from app.sockets import socket_auth
from app.models.user import User
from app.models.course import Course
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.lesson_attachment import LessonAttachment
from app.models.enrollment import Enrollment
from app.models.review import Review, ReviewStatus
from app.models.review_report import ReviewReport
from app.models.qa_message import QAMessage
from app.models.progress import Progress
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.option import Option
from app.models.quiz_attempt import QuizAttempt
from app.models.question_thread import QuestionThread
from app.models.answer import Answer
from app.models.payment import Payment, PaymentStatus

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
from app.routes.qa_routes import qa_bp
from app.routes.certificate_routes import certificate_bp
from app.routes.announcement_routes import announcement_bp
from app.routes.payment_routes import payment_bp
from app.routes.search_routes import search_bp

import os
from flask import send_from_directory

def create_app(config=None):
    app = Flask(__name__)

    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(Config)

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    )
    CORS(app, resources={
    r"/api/*": {
        "origins": [frontend_url],
        "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
        }
    })
    

    @app.after_request
    def after_request(response):
        response.headers["Access-Control-Allow-Origin"] = frontend_url
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE,OPTIONS,PATCH"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    db.init_app(app)
    from sqlalchemy import text

    with app.app_context():
        print("=" * 50)
        print("DATABASE URI:", app.config["SQLALCHEMY_DATABASE_URI"])

        result = db.session.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            ORDER BY table_name;
        """))

        print("TABLES:")
        for row in result:
            print(row[0])

        print("=" * 50)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    stripe.api_key = app.config.get("STRIPE_SECRET_KEY")
    redis_url = app.config.get("REDIS_URL")
    if redis_url:
        import redis
        try:
            r = redis.Redis.from_url(redis_url, socket_timeout=1.0)
            r.ping()
            app.logger.info("Successfully connected to Redis. Using Redis for Socket.IO message queue.")
        except Exception as e:
            app.logger.warning(f"Redis connection failed ({e}). Falling back to in-memory message queue.")
            redis_url = None

    socketio.init_app(
        app,
        cors_allowed_origins=frontend_url,
        async_mode="threading",
        message_queue=redis_url,
        logger=True,
        engineio_logger=True
    )
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
    app.register_blueprint(notification_bp)
    app.register_blueprint(qa_bp)
    app.register_blueprint(announcement_bp)
    app.register_blueprint(certificate_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(search_bp)

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(
            os.path.join(app.root_path, 'uploads'), filename
        )

    return app