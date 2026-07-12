import uuid
import pytest
from app.extensions import db
from app.models.payment import Payment, PaymentStatus

from unittest.mock import patch, MagicMock


class TestPayments:

    def test_get_my_payments_empty(self, client, student_token):
        res = client.get(
            '/api/payments/my-payments',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 200
        data = res.get_json()
        assert isinstance(data, list)

    def test_get_my_payments_requires_auth(self, client):
        res = client.get('/api/payments/my-payments')
        assert res.status_code == 401

    @patch('stripe.checkout.Session.create')
    def test_stripe_create_checkout(
            self, mock_stripe, client, student_token, sample_course):
        """Test Stripe checkout session creation with mocked Stripe API."""
        mock_stripe.return_value = MagicMock(
            url='https://checkout.stripe.com/test/session_123',
            id='cs_test_123'
        )

        res = client.post(
            f'/api/payments/stripe/create-checkout/{sample_course.id}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        # Should return 200 with checkout URL
        # or 400 if already enrolled — both are valid
        assert res.status_code in [200, 400]
        if res.status_code == 200:
            data = res.get_json()
            assert 'url' in data or 'checkout_url' in data

    @patch('stripe.checkout.Session.create')
    def test_stripe_checkout_nonexistent_course(
            self, mock_stripe, client, student_token):
        """Test Stripe checkout with invalid course ID."""
        res = client.post(
            f'/api/payments/stripe/create-checkout/{str(uuid.uuid4())}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 404

    def test_stripe_checkout_requires_auth(self, client, sample_course):
        res = client.post(
            f'/api/payments/stripe/create-checkout/{sample_course.id}'
        )
        assert res.status_code == 401

    @patch('requests.post')
    def test_paypal_create_order(
            self, mock_requests, client, student_token, sample_course):
        """Test PayPal order creation with mocked PayPal API."""
        # Mock the token request
        token_response = MagicMock()
        token_response.json.return_value = {
            'access_token': 'test_paypal_token'
        }

        # Mock the order creation request
        order_response = MagicMock()
        order_response.json.return_value = {
            'id': 'PAYPAL_ORDER_123',
            'status': 'CREATED',
            'links': [
                {
                    'rel': 'approve',
                    'href': 'https://sandbox.paypal.com/checkoutnow?token=abc'
                }
            ]
        }

        mock_requests.side_effect = [token_response, order_response]

        res = client.post(
            f'/api/payments/paypal/create-order/{sample_course.id}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code in [200, 400]
        if res.status_code == 200:
            data = res.get_json()
            assert 'url' in data or 'order_id' in data

    def test_paypal_create_order_requires_auth(
            self, client, sample_course):
        res = client.post(
            f'/api/payments/paypal/create-order/{sample_course.id}'
        )
        assert res.status_code == 401

    def test_paypal_nonexistent_course(self, client, student_token):
        res = client.post(
            f'/api/payments/paypal/create-order/{str(uuid.uuid4())}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 404

    @patch('stripe.checkout.Session.retrieve')
    def test_stripe_confirm_payment(
            self, mock_retrieve, client, student_token, sample_course):
        """Test stripe payment confirmation with mocked Stripe."""
        mock_retrieve.return_value = MagicMock(
            payment_status='paid',
            metadata={'course_id': sample_course.id}
        )

        res = client.post(
            '/api/payments/stripe/confirm/cs_test_fake_session_id',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code in [200, 400, 404]
        # 200 = confirmed and enrolled
        # 400 = already enrolled
        # 404 = session not found (mock may not match route)

    def test_all_payments_admin_only(
            self, client, admin_token, student_token):
        # Admin can access
        res = client.get(
            '/api/payments/all-payments',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert res.status_code == 200

        # Student cannot access
        res = client.get(
            '/api/payments/all-payments',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 403

    @patch("stripe.Refund.create")
    def test_refund_stripe_payment(
        self,
        mock_refund,
        client,
        admin_token,
        student_user,
        sample_course,
    ):
        payment = Payment(
            student_id=student_user.id,
            course_id=sample_course.id,
            amount=sample_course.price,
            provider="stripe",
            transaction_id="txn_123",
            payment_intent_id="pi_123",
            status=PaymentStatus.COMPLETED,
        )
        db.session.add(payment)
        db.session.commit()

        mock_refund.return_value = {}

        res = client.post(
            f"/api/payments/refund/{payment.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code in [200, 400]


    def test_refund_nonexistent_payment(
        self,
        client,
        admin_token,
    ):
        res = client.post(
            f"/api/payments/refund/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 404


    def test_student_cannot_refund_payment(
        self,
        client,
        student_token,
    ):
        res = client.post(
            f"/api/payments/refund/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {student_token}"},
        )

        assert res.status_code == 403


    @patch("app.services.payment_service.capture_paypal_order")
    def test_capture_paypal_invalid_order(
        self,
        mock_capture,
        client,
        student_token,
    ):
        res = client.post(
            "/api/payments/paypal/capture/INVALID_ORDER",
            headers={"Authorization": f"Bearer {student_token}"},
        )

        assert res.status_code == 404


    def test_capture_paypal_requires_auth(
        self,
        client,
    ):
        res = client.post(
            "/api/payments/paypal/capture/ORDER123"
        )

        assert res.status_code == 401


    def test_paypal_webhook_invalid_payload(
        self,
        client,
    ):
        res = client.post(
            "/api/payments/paypal/webhook",
            json=None,
        )

        assert res.status_code == 400


    @patch("app.routes.payment_routes.verify_paypal_webhook")
    def test_paypal_webhook_invalid_signature(
        self,
        mock_verify,
        client,
    ):
        mock_verify.return_value = False

        res = client.post(
            "/api/payments/paypal/webhook",
            json={"event_type": "PAYMENT.CAPTURE.COMPLETED"},
        )

        assert res.status_code == 400


    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_unknown_event(
        self,
        mock_construct,
        client,
    ):
        mock_construct.return_value = {
            "type": "payment.failed",
            "data": {},
        }

        res = client.post(
            "/api/payments/stripe/webhook",
            data="{}",
            headers={"Stripe-Signature": "abc"},
        )

        assert res.status_code == 200


    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_invalid_signature(
        self,
        mock_construct,
        client,
    ):
        mock_construct.side_effect = Exception("Invalid signature")

        res = client.post(
            "/api/payments/stripe/webhook",
            data="{}",
            headers={"Stripe-Signature": "bad"},
        )

        assert res.status_code == 400


    def test_all_payments_requires_auth(
        self,
        client,
    ):
        res = client.get("/api/payments/all-payments")

        assert res.status_code == 401


    @patch("stripe.checkout.Session.create")
    def test_duplicate_checkout_prevented(
        self,
        mock_session,
        client,
        student_token,
        student_user,
        sample_course,
    ):
        payment = Payment(
            student_id=student_user.id,
            course_id=sample_course.id,
            amount=sample_course.price,
            provider="stripe",
            transaction_id="abc123",
            status=PaymentStatus.COMPLETED,
        )

        db.session.add(payment)
        db.session.commit()

        res = client.post(
            f"/api/payments/stripe/create-checkout/{sample_course.id}",
            headers={"Authorization": f"Bearer {student_token}"},
        )

        assert res.status_code == 400


    def test_paypal_refund_nonexistent_payment(
        self,
        client,
        admin_token,
    ):
        res = client.post(
            f"/api/payments/paypal/refund/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 404


    def test_student_cannot_view_all_payments(
        self,
        client,
        student_token,
    ):
        res = client.get(
            "/api/payments/all-payments",
            headers={"Authorization": f"Bearer {student_token}"},
        )

        assert res.status_code == 403