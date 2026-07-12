import base64
from urllib import response

import requests
import stripe
from flask import current_app
from app.extensions import db
from app.models.enrollment import Enrollment
from app.models.payment import Payment, PaymentStatus


def init_stripe():
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]


def get_paypal_api_base():
    if current_app.config.get("PAYPAL_MODE", "sandbox") == "live":
        return "https://api-m.paypal.com"
    return "https://api-m.sandbox.paypal.com"


def get_paypal_access_token():
    auth = base64.b64encode(
        (
            f"{current_app.config['PAYPAL_CLIENT_ID']}:"
            f"{current_app.config['PAYPAL_CLIENT_SECRET']}"
        ).encode()
    ).decode()

    response = requests.post(
        f"{get_paypal_api_base()}/v1/oauth2/token",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def paypal_request(method, path, **kwargs):
    access_token = get_paypal_access_token()
    response = requests.request(
        method,
        f"{get_paypal_api_base()}{path}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        timeout=30,
        **kwargs,
    )
    return response


def create_paypal_order(course, user_id, payment_id):
    response = paypal_request(
        "POST",
        "/v2/checkout/orders",
        json={
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": payment_id,
                    "custom_id": f"{user_id}:{course.id}",
                    "amount": {
                        "currency_code": "USD",
                        "value": f"{course.price:.2f}",
                    },
                    "description": course.title,
                }
            ],
            "application_context": {
                "return_url": (
                    f"{current_app.config['FRONTEND_URL']}/success?provider=paypal"
                ),
                "cancel_url": (
                    f"{current_app.config['FRONTEND_URL']}/cancel"
                ),
            },
        },
    )
    print("STATUS:", response.status_code)
    print("BODY:", response.text)

    if response.status_code >= 400:
        raise Exception(response.text)

    return response.json()

def capture_paypal_order(order_id):
    response = paypal_request(
        "POST",
        f"/v2/checkout/orders/{order_id}/capture",
        json={},
    )
    return response


def refund_paypal_capture(capture_id, amount=None):
    payload = {}
    if amount is not None:
        payload["amount"] = {
            "value": f"{amount:.2f}",
            "currency_code": "USD",
        }

    response = paypal_request(
        "POST",
        f"/v2/payments/captures/{capture_id}/refund",
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def verify_paypal_webhook(headers, event):
    webhook_id = current_app.config.get("PAYPAL_WEBHOOK_ID")
    if not webhook_id:
        return current_app.config.get("PAYPAL_MODE", "sandbox") == "sandbox"

    transmission_id = headers.get("PAYPAL-TRANSMISSION-ID")
    transmission_time = headers.get("PAYPAL-TRANSMISSION-TIME")
    cert_url = headers.get("PAYPAL-CERT-URL")
    auth_algo = headers.get("PAYPAL-AUTH-ALGO")
    transmission_sig = headers.get("PAYPAL-TRANSMISSION-SIG")

    if not all(
        [
            transmission_id,
            transmission_time,
            cert_url,
            auth_algo,
            transmission_sig,
        ]
    ):
        return False

    response = paypal_request(
        "POST",
        "/v1/notifications/verify-webhook-signature",
        json={
            "auth_algo": auth_algo,
            "cert_url": cert_url,
            "transmission_id": transmission_id,
            "transmission_sig": transmission_sig,
            "transmission_time": transmission_time,
            "webhook_id": webhook_id,
            "webhook_event": event,
        },
    )
    if response.status_code != 200:
        return False

    return response.json().get("verification_status") == "SUCCESS"


def has_course_access(student_id, course_id):
    return Enrollment.query.filter_by(
        student_id=student_id,
        course_id=course_id,
    ).first() is not None


def has_completed_payment(student_id, course_id):
    return Payment.query.filter_by(
        student_id=student_id,
        course_id=course_id,
        status=PaymentStatus.COMPLETED,
    ).first() is not None


def grant_enrollment(student_id, course_id):
    if has_course_access(student_id, course_id):
        return

    db.session.add(
        Enrollment(
            student_id=student_id,
            course_id=course_id,
        )
    )


def revoke_enrollment(student_id, course_id):
    Enrollment.query.filter_by(
        student_id=student_id,
        course_id=course_id,
    ).delete()


def get_stripe_payment_intent(payment):
    if payment.payment_intent_id:
        return payment.payment_intent_id

    session = stripe.checkout.Session.retrieve(
        payment.transaction_id
    )
    payment_intent = session.payment_intent
    if payment_intent:
        payment.payment_intent_id = payment_intent
    return payment_intent


def complete_stripe_payment(payment, payment_intent_id=None):
    payment.status = PaymentStatus.COMPLETED
    if payment_intent_id:
        payment.payment_intent_id = payment_intent_id
    grant_enrollment(payment.student_id, payment.course_id)
    current_app.logger.info(f"Enrollment granted: student {payment.student_id} -> course {payment.course_id}")


def rollback_payment_entitlement(payment, status):
    payment.status = status
    revoke_enrollment(payment.student_id, payment.course_id)


def extract_paypal_capture_id(capture_payload):
    if capture_payload.get("id"):
        return capture_payload["id"]

    purchase_units = capture_payload.get("purchase_units", [])
    for unit in purchase_units:
        captures = unit.get("payments", {}).get("captures", [])
        if captures:
            return captures[0]["id"]

    return None


def find_paypal_payment(order_id=None, capture_id=None):
    if order_id:
        payment = Payment.query.filter_by(
            order_id=order_id,
            provider="paypal",
        ).first()
        if payment:
            return payment

        payment = Payment.query.filter_by(
            transaction_id=order_id,
            provider="paypal",
        ).first()
        if payment:
            return payment

    if capture_id:
        return Payment.query.filter_by(
            payment_intent_id=capture_id,
            provider="paypal",
        ).first()

    return None


def notify_payment_refund(payment):
    from app.models.course import Course
    from app.models.user import User
    from app.services.email_service import send_email
    from app.services.notification_service import create_notification

    course = Course.query.get(payment.course_id)
    student = User.query.get(payment.student_id)
    if not course or not student:
        return

    title = "Refund Processed"
    message = f"Your payment for '{course.title}' has been refunded."

    create_notification(payment.student_id, title, message)
    send_email(student.email, title, message)
