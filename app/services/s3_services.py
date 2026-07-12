import uuid

import boto3

from flask import current_app


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        region_name=current_app.config["AWS_REGION"],
    )


def upload_file(file, folder):
    return upload_fileobj(
        file,
        file.filename,
        folder,
    )


def upload_fileobj(file_obj, filename, folder="certificates"):
    key = f"{folder}/{uuid.uuid4()}_{filename}"

    s3 = get_s3_client()
    s3.upload_fileobj(
        file_obj,
        current_app.config["AWS_BUCKET_NAME"],
        key,
    )

    return key


def extract_s3_key(url_or_key):
    if not url_or_key:
        return None

    if not url_or_key.startswith("http"):
        return url_or_key

    bucket = current_app.config["AWS_BUCKET_NAME"]
    region = current_app.config["AWS_REGION"]
    prefix = f"https://{bucket}.s3.{region}.amazonaws.com/"

    if url_or_key.startswith(prefix):
        return url_or_key[len(prefix):]

    if ".amazonaws.com/" in url_or_key:
        return url_or_key.split(".amazonaws.com/", 1)[-1]

    return url_or_key


def generate_presigned_url(key, expires_in=None):
    if not key:
        return None

    expires_in = expires_in or current_app.config.get(
        "S3_PRESIGNED_URL_EXPIRES",
        3600,
    )

    s3 = get_s3_client()
    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": current_app.config["AWS_BUCKET_NAME"],
            "Key": key,
        },
        ExpiresIn=expires_in,
    )


def resolve_media_url(stored_value):
    key = extract_s3_key(stored_value)
    if not key:
        return None

    return generate_presigned_url(key)
