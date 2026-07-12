import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Database
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL")
        or os.getenv("SQLALCHEMY_DATABASE_URI")
        or "postgresql://localhost/your_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")

    # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

    # PayPal
    PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
    PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
    PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")
    PAYPAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID")

    # AWS
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
    AWS_REGION = os.getenv("AWS_REGION")

    # Mail
    MAIL_SUPPRESS_SEND = (
        os.getenv("MAIL_SUPPRESS_SEND", "False").lower() == "true"
    )
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # Redis
    REDIS_URL = os.getenv("REDIS_URL")

    # Frontend
    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000"
    )

    # Elasticsearch
    ELASTICSEARCH_URL = os.getenv(
        "ELASTICSEARCH_URL",
        "http://localhost:9200"
    )
    ELASTICSEARCH_ENABLED = (
        os.getenv("ELASTICSEARCH_ENABLED", "true").lower() == "true"
    )

    # S3
    S3_PRESIGNED_URL_EXPIRES = int(
        os.getenv("S3_PRESIGNED_URL_EXPIRES", 3600)
    )


class TestConfig(Config):
    TESTING = True

    # Use an in-memory SQLite database
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Test secrets
    JWT_SECRET_KEY = "test-secret-key-for-testing-only-32chars-long"
    STRIPE_SECRET_KEY = "sk_test_fake"

    # Disable external services
    MAIL_SUPPRESS_SEND = True
    REDIS_URL = None

    # Disable CSRF for tests
    WTF_CSRF_ENABLED = False