import uuid
import os
import boto3
from botocore.config import Config


def _get_boto_config():
    """
    Use urllib3 directly without gevent's monkey-patched SSL.
    This fixes the RecursionError on Render with gevent.
    """
    return Config(
        retries={'max_attempts': 3},
        connect_timeout=30,
        read_timeout=300,
    )


def get_s3_client():
    # Temporarily unpatch SSL if gevent has patched it
    try:
        import gevent.monkey
        if gevent.monkey.is_module_patched('ssl'):
            import ssl
            import _ssl
            # Restore original SSL before boto3 call
            ssl.SSLContext = _ssl._SSLContext
    except Exception:
        pass

    return boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
        config=_get_boto_config(),
    )


def upload_file(file, folder):
    return upload_fileobj(file, file.filename, folder)


def upload_fileobj(file_obj, filename, folder="certificates"):
    key = f"{folder}/{uuid.uuid4()}_{filename}"
    s3 = get_s3_client()
    bucket = os.environ.get("AWS_BUCKET_NAME")
    s3.upload_fileobj(file_obj, bucket, key)
    return key


def extract_s3_key(url_or_key):
    if not url_or_key:
        return None
    if not url_or_key.startswith("http"):
        return url_or_key
    bucket = os.environ.get("AWS_BUCKET_NAME")
    region = os.environ.get("AWS_REGION", "us-east-1")
    prefix = f"https://{bucket}.s3.{region}.amazonaws.com/"
    if url_or_key.startswith(prefix):
        return url_or_key[len(prefix):]
    if ".amazonaws.com/" in url_or_key:
        return url_or_key.split(".amazonaws.com/", 1)[-1]
    return url_or_key


def generate_presigned_url(key, expires_in=3600):
    if not key:
        return None
    s3 = get_s3_client()
    bucket = os.environ.get("AWS_BUCKET_NAME")
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )


def resolve_media_url(stored_value):
    key = extract_s3_key(stored_value)
    if not key:
        return None
    return generate_presigned_url(key)