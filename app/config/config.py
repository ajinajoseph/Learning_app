import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    AWS_ACCESS_KEY_ID = os.getenv(
    "AWS_ACCESS_KEY_ID"
    )

    AWS_SECRET_ACCESS_KEY = os.getenv(
    "AWS_SECRET_ACCESS_KEY"
    )

    AWS_BUCKET_NAME = os.getenv(
    "AWS_BUCKET_NAME"
    )

    AWS_REGION = os.getenv(
    "AWS_REGION"
     )