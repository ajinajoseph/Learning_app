import uuid

import boto3

from flask import current_app


def get_s3_client():

    return boto3.client(
        "s3",
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        region_name=current_app.config["AWS_REGION"]
    )


def upload_file(file, folder):

    filename = (
        f"{folder}/"
        f"{uuid.uuid4()}_"
        f"{file.filename}"
    )

    s3 = get_s3_client()

    s3.upload_fileobj(
        file,
        current_app.config["AWS_BUCKET_NAME"],
        filename
    )

    return (
        f"https://"
        f"{current_app.config['AWS_BUCKET_NAME']}.s3."
        f"{current_app.config['AWS_REGION']}.amazonaws.com/"
        f"{filename}"
    )