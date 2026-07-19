from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import stripe
import os

from app.extensions import db
from app.middleware.role_required import role_required
from app.models.course import Course
from app.models.payment import Payment, PaymentStatus
from app.models.user import UserRole
from app.services.payment_service import (
    capture_paypal_order,
    complete_stripe_payment,
    create_paypal_order,
    extract_paypal_capture_id,
    find_paypal_payment,
    get_stripe_payment_intent,
    grant_enrollment,
    has_completed_payment,
    notify_payment_refund,
    refund_paypal_capture,
    rollback_payment_entitlement,
    verify_paypal_webhook,
)


payment_bp = Blueprint(
    "payment",
    __name__,
    url_prefix="/api/payments",
)


def _course_or_404(course_id):
    course = Course.query.get(course_id)
    if not course:
        return None, (jsonify({"message": "Course not found"}), 404)
    return course, None


def _block_if_already_paid(user_id, course_id):
    if has_completed_payment(user_id, course_id):
        return jsonify({"message": "Course already purchased"}), 400
    return None


@payment_bp.route(
    "/stripe/create-checkout/<course_id>",
    methods=["POST"],
)
@jwt_required()
@role_required(UserRole.STUDENT)
def create_stripe_checkout(course_id):
    user_id = get_jwt_identity()
    course, error = _course_or_404(course_id)
    if error:
        return error

    blocked = _block_if_already_paid(user_id, course_id)
    if blocked:
        return blocked

    frontend_url = os.getenv("FRONTEND_URL", current_app.config.get("FRONTEND_URL", "http://localhost:5173"))
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": course.title},
                    "unit_amount": int(course.price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=f"{frontend_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{frontend_url}/courses",
        metadata={
            "course_id": str(course_id),
        },
    )

    payment = Payment(
        student_id=user_id,
        course_id=course_id,
        amount=course.price,
        provider="stripe",
        transaction_id=session.id,
        status=PaymentStatus.PENDING,
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({
        "checkout_url": session.url,
        "payment_id": payment.id,
    }), 200


@payment_bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    # Verify webhook signature
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except Exception as e:
        current_app.logger.error(f"Stripe webhook error: {e}")
        return jsonify({"message": "Invalid webhook signature"}), 400

    # Handle successful checkout session
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Retrieve the payment record using the checkout session ID
        payment = Payment.query.filter_by(transaction_id=session["id"]).first()
        if not payment:
            current_app.logger.error("Payment record not found for session %s", session["id"])
            return jsonify({"message": "Payment not found"}), 404
        if payment.status == PaymentStatus.COMPLETED:
            return jsonify({
                "message": "Payment already processed"
            }), 200
        try:
            complete_stripe_payment(payment, payment_intent_id=session.get("payment_intent"))
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            current_app.logger.error("Error completing Stripe payment: %s", exc)
            return jsonify({"message": str(exc)}), 500

        return jsonify({"message": "Payment successful and enrollment granted"}), 200

    # For other event types, just acknowledge
    return jsonify({"message": "Event ignored"}), 200

@payment_bp.route("/stripe/confirm/<session_id>", methods=["POST"])
@jwt_required()
def confirm_stripe_payment(session_id):
    try:
        # Retrieve checkout session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)

        # Find corresponding payment in database
        payment = Payment.query.filter_by(
            transaction_id=session.id
        ).first()

        if not payment:
            return jsonify({
                "success": False,
                "message": "Payment not found"
            }), 404

        # Payment has been successfully completed on Stripe
        if session.payment_status == "paid":

            # Prevent duplicate processing
            if payment.status != PaymentStatus.COMPLETED:
                complete_stripe_payment(
                    payment,
                    payment_intent_id=session.payment_intent
                )
                db.session.commit()

            return jsonify({
                "success": True,
                "course_id": payment.course_id
            }), 200

        # Payment still pending
        return jsonify({
            "success": False,
            "message": "Payment is still processing. Please wait a few seconds and try again."
        }), 202

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Stripe confirmation failed")

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@payment_bp.route("/refund/<payment_id>", methods=["POST"])
@jwt_required()
@role_required(UserRole.ADMIN)
def refund_payment(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({"message": "Payment not found"}), 404

    if payment.status != PaymentStatus.COMPLETED:
        return jsonify({
            "message": "Only completed payments can be refunded",
        }), 400

    if payment.provider != "stripe":
        return jsonify({
            "message": "Use the PayPal refund endpoint for PayPal payments",
        }), 400

    try:
        payment_intent_id = get_stripe_payment_intent(payment)
        if not payment_intent_id:
            return jsonify({"message": "Payment intent not found"}), 400

        stripe.Refund.create(payment_intent=payment_intent_id)
        rollback_payment_entitlement(payment, PaymentStatus.REFUNDED)
        db.session.commit()
        notify_payment_refund(payment)

        return jsonify({"message": "Refund successful"}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"message": str(exc)}), 400


@payment_bp.route("/paypal/create-order/<course_id>", methods=["POST"])
@jwt_required()
@role_required(UserRole.STUDENT)
def create_paypal_order_route(course_id):
    user_id = get_jwt_identity()
    course, error = _course_or_404(course_id)
    if error:
        return error

    blocked = _block_if_already_paid(user_id, course_id)
    if blocked:
        return blocked

    payment = Payment(
        student_id=user_id,
        course_id=course_id,
        amount=course.price,
        provider="paypal",
        status=PaymentStatus.PENDING,
    )
    db.session.add(payment)
    db.session.flush()

    try:
        order_data = create_paypal_order(course, user_id, payment.id)
    except Exception as exc:
        db.session.rollback()
        return jsonify({"message": str(exc)}), 400

    payment.order_id = order_data["id"]
    payment.transaction_id = order_data["id"]
    db.session.commit()

    approve_url = next(
        link["href"]
        for link in order_data["links"]
        if link["rel"] == "approve"
    )

    return jsonify({
        "order_id": order_data["id"],
        "approve_url": approve_url,
        "payment_id": payment.id,
    }), 200


@payment_bp.route("/paypal/capture/<order_id>", methods=["POST"])
@jwt_required()
@role_required(UserRole.STUDENT)
def capture_paypal(order_id):
    user_id = get_jwt_identity()

    payment = Payment.query.filter_by(
        order_id=order_id,
        provider="paypal",
        student_id=user_id,
    ).first()

    if not payment:
        payment = Payment.query.filter_by(
            transaction_id=order_id,
            provider="paypal",
            student_id=user_id,
        ).first()

    if not payment:
        return jsonify({"message": "Payment not found"}), 404

    if payment.status == PaymentStatus.COMPLETED:
        return jsonify({"message": "Payment already completed"}), 200

    try:
        capture_res = capture_paypal_order(order_id)
        result = capture_res.json()
    except Exception as exc:
        return jsonify({"message": str(exc)}), 400

    if capture_res.status_code >= 400 or result.get("status") != "COMPLETED":
        payment.status = PaymentStatus.FAILED
        db.session.commit()
        return jsonify({
            "message": result.get("message", "Payment failed"),
        }), 400

    capture_id = extract_paypal_capture_id(result)
    payment.payment_intent_id = capture_id

    if not current_app.config.get("PAYPAL_WEBHOOK_ID"):
        payment.status = PaymentStatus.COMPLETED
        grant_enrollment(payment.student_id, payment.course_id)

    db.session.commit()

    message = (
        "Payment captured, awaiting webhook confirmation"
        if current_app.config.get("PAYPAL_WEBHOOK_ID")
        else "Payment successful"
    )
    return jsonify({"message": message}), 200


@payment_bp.route("/paypal/webhook", methods=["POST"])
def paypal_webhook():
    event = request.get_json(silent=True)
    if not event:
        return jsonify({"message": "Invalid payload"}), 400

    if not verify_paypal_webhook(dict(request.headers), event):
        return jsonify({"message": "Invalid webhook signature"}), 400

    event_type = event.get("event_type")
    resource = event.get("resource", {})

    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        order_id = resource.get("supplementary_data", {}).get(
            "related_ids", {}
        ).get("order_id")
        custom_id = resource.get("custom_id")
        capture_id = resource.get("id")

        payment = find_paypal_payment(order_id=order_id, capture_id=capture_id)

        if not payment and custom_id and ":" in custom_id:
            student_id, course_id = custom_id.split(":", 1)
            payment = Payment.query.filter_by(
                student_id=student_id,
                course_id=course_id,
                provider="paypal",
                status=PaymentStatus.PENDING,
            ).first()

        if payment and payment.status != PaymentStatus.COMPLETED:
            payment.payment_intent_id = capture_id
            payment.status = PaymentStatus.COMPLETED
            grant_enrollment(payment.student_id, payment.course_id)
            db.session.commit()

    elif event_type in (
        "PAYMENT.CAPTURE.REFUNDED",
        "PAYMENT.CAPTURE.REVERSED",
    ):
        payment = find_paypal_payment(capture_id=resource.get("id"))
        if payment and payment.status == PaymentStatus.COMPLETED:
            rollback_payment_entitlement(payment, PaymentStatus.REFUNDED)
            db.session.commit()
            notify_payment_refund(payment)

    elif event_type == "CUSTOMER.DISPUTE.CREATED":
        disputed_transactions = resource.get("disputed_transactions", [])
        capture_id = None
        if disputed_transactions:
            capture_id = disputed_transactions[0].get(
                "seller_transaction_id"
            )

        payment = find_paypal_payment(capture_id=capture_id)
        if payment and payment.status == PaymentStatus.COMPLETED:
            rollback_payment_entitlement(payment, PaymentStatus.DISPUTED)
            db.session.commit()

    return jsonify({"message": "Webhook processed"}), 200


@payment_bp.route("/paypal/refund/<payment_id>", methods=["POST"])
@jwt_required()
@role_required(UserRole.ADMIN)
def paypal_refund(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({"message": "Payment not found"}), 404

    if payment.provider != "paypal":
        return jsonify({
            "message": "Use the Stripe refund endpoint for Stripe payments",
        }), 400

    if payment.status != PaymentStatus.COMPLETED:
        return jsonify({
            "message": "Only completed payments can be refunded",
        }), 400

    capture_id = payment.payment_intent_id
    if not capture_id:
        return jsonify({"message": "Capture ID not found"}), 400

    try:
        refund_paypal_capture(capture_id, payment.amount)
        rollback_payment_entitlement(payment, PaymentStatus.REFUNDED)
        db.session.commit()
        notify_payment_refund(payment)
        return jsonify({"message": "Refund successful"}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"message": str(exc)}), 400


@payment_bp.route("/my-payments", methods=["GET"])
@jwt_required()
@role_required(UserRole.STUDENT)
def my_payments():
    user_id = get_jwt_identity()
    payments = Payment.query.filter_by(student_id=user_id).all()
    return jsonify([payment.to_dict() for payment in payments]), 200


@payment_bp.route("/all-payments", methods=["GET"])
@jwt_required()
@role_required(UserRole.ADMIN)
def all_payments():
    payments = Payment.query.all()
    return jsonify([payment.to_dict() for payment in payments]), 200
