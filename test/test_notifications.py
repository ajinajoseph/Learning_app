from app.extensions import db
from app.models.notification import Notification
from app.models.user import User, UserRole
import uuid


class TestNotificationRoutes:

    def test_get_notifications(
        self,
        client,
        student_token,
        student_user,
    ):
        notification = Notification(
            user_id=student_user.id,
            title="New Lesson",
            message="Lesson added"
        )

        db.session.add(notification)
        db.session.commit()

        res = client.get(
            "/api/notifications",
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 200

        data = res.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "New Lesson"
        assert data[0]["message"] == "Lesson added"
        assert data[0]["is_read"] is False

    def test_get_notifications_empty(
        self,
        client,
        student_token,
    ):
        res = client.get(
            "/api/notifications",
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 200
        assert res.get_json() == []

    def test_get_notifications_requires_auth(
        self,
        client,
    ):
        res = client.get("/api/notifications")

        assert res.status_code == 401

    def test_mark_notification_read(
        self,
        client,
        student_token,
        student_user,
    ):
        notification = Notification(
            user_id=student_user.id,
            title="Notification",
            message="Test"
        )

        db.session.add(notification)
        db.session.commit()

        res = client.put(
            f"/api/notifications/read/{notification.id}",
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 200
        assert res.get_json()["message"] == "Notification marked as read"

        db.session.refresh(notification)
        assert notification.is_read is True

    def test_mark_notification_not_found(
        self,
        client,
        student_token,
    ):
        res = client.put(
            "/api/notifications/read/invalid-id",
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 404
        assert res.get_json()["message"] == "Notification not found"

    def test_mark_notification_access_denied(
        self,
        client,
        app,
        student_token,
        mentor_user,
    ):
        notification = Notification(
            user_id=mentor_user.id,
            title="Private",
            message="Hidden"
        )

        db.session.add(notification)
        db.session.commit()

        res = client.put(
            f"/api/notifications/read/{notification.id}",
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 403
        assert res.get_json()["message"] == "Access denied"

    def test_mark_notification_requires_auth(
        self,
        client,
        student_user,
    ):
        notification = Notification(
            user_id=student_user.id,
            title="Test",
            message="Test"
        )

        db.session.add(notification)
        db.session.commit()

        res = client.put(
            f"/api/notifications/read/{notification.id}"
        )

        assert res.status_code == 401

    def test_unread_count(
        self,
        client,
        student_token,
        student_user,
    ):
        db.session.add_all([
            Notification(
                user_id=student_user.id,
                title="One",
                message="One",
                is_read=False,
            ),
            Notification(
                user_id=student_user.id,
                title="Two",
                message="Two",
                is_read=False,
            ),
            Notification(
                user_id=student_user.id,
                title="Three",
                message="Three",
                is_read=True,
            ),
        ])

        db.session.commit()

        res = client.get(
            "/api/notifications/unread-count",
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 200
        assert res.get_json()["unread_count"] == 2

    def test_unread_count_zero(
        self,
        client,
        student_token,
    ):
        res = client.get(
            "/api/notifications/unread-count",
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 200
        assert res.get_json()["unread_count"] == 0

    def test_unread_count_requires_auth(
        self,
        client,
    ):
        res = client.get(
            "/api/notifications/unread-count"
        )

        assert res.status_code == 401