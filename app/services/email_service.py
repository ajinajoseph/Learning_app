from threading import Thread
from flask import current_app
from flask_mail import Message

from app.extensions import mail


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Failed to send email to {msg.recipients}: {e}")


def send_email(
    recipient,
    subject,
    body
):

    msg = Message(
        subject=subject,
        recipients=[recipient]
    )

    msg.body = body

    try:
        app = current_app._get_current_object()
        thr = Thread(target=send_async_email, args=[app, msg])
        thr.start()
    except Exception as e:
        # Fallback to synchronous if context is missing or threading fails
        try:
            mail.send(msg)
        except Exception as mail_err:
            current_app.logger.error(f"Fallback email sending failed: {mail_err}")