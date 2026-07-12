from app.models.announcement import Announcement


class TestAnnouncements:

    def test_create_announcement(
        self,
        client,
        mentor_token,
        sample_course,
    ):
        res = client.post(
            "/api/announcements",
            json={
                "course_id": sample_course.id,
                "title": "Holiday",
                "message": "No class tomorrow",
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 201
        assert res.json["title"] == "Holiday"

    def test_create_announcement_invalid_course(
        self,
        client,
        mentor_token,
    ):
        res = client.post(
            "/api/announcements",
            json={
                "course_id": "invalid-id",
                "title": "Holiday",
                "message": "No class",
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 404

    def test_student_cannot_create_announcement(
        self,
        client,
        student_token,
        sample_course,
    ):
        res = client.post(
            "/api/announcements",
            json={
                "course_id": sample_course.id,
                "title": "Test",
                "message": "Test message",
            },
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 403

    def test_create_announcement_requires_auth(
        self,
        client,
        sample_course,
    ):
        res = client.post(
            "/api/announcements",
            json={
                "course_id": sample_course.id,
                "title": "Test",
                "message": "Test",
            },
        )

        assert res.status_code == 401

    def test_get_announcements(
        self,
        client,
        db,
        sample_course,
    ):
        announcement = Announcement(
            course_id=sample_course.id,
            title="Announcement",
            message="Welcome",
        )

        db.session.add(announcement)
        db.session.commit()

        res = client.get(
            f"/api/announcements/{sample_course.id}"
        )

        assert res.status_code == 200
        assert len(res.json) >= 1

    def test_update_announcement(
        self,
        client,
        db,
        mentor_token,
        sample_course,
    ):
        announcement = Announcement(
            course_id=sample_course.id,
            title="Old",
            message="Old Message",
        )

        db.session.add(announcement)
        db.session.commit()

        res = client.put(
            f"/api/announcements/{announcement.id}",
            json={
                "title": "New Title",
                "message": "Updated Message",
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 200
        assert res.json["title"] == "New Title"

    def test_update_invalid_announcement(
        self,
        client,
        mentor_token,
    ):
        res = client.put(
            "/api/announcements/invalid-id",
            json={
                "title": "New",
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 404

    def test_update_requires_auth(
        self,
        client,
        db,
        sample_course,
    ):
        announcement = Announcement(
            course_id=sample_course.id,
            title="Old",
            message="Old",
        )

        db.session.add(announcement)
        db.session.commit()

        res = client.put(
            f"/api/announcements/{announcement.id}",
            json={
                "title": "Updated",
            },
        )

        assert res.status_code == 401

    def test_student_cannot_update_announcement(
        self,
        client,
        db,
        student_token,
        sample_course,
    ):
        announcement = Announcement(
            course_id=sample_course.id,
            title="Old",
            message="Old",
        )

        db.session.add(announcement)
        db.session.commit()

        res = client.put(
            f"/api/announcements/{announcement.id}",
            json={
                "title": "Updated",
            },
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 403

    def test_delete_announcement(
        self,
        client,
        db,
        mentor_token,
        sample_course,
    ):
        announcement = Announcement(
            course_id=sample_course.id,
            title="Delete",
            message="Delete Me",
        )

        db.session.add(announcement)
        db.session.commit()

        res = client.delete(
            f"/api/announcements/{announcement.id}",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 200
        assert res.json["message"] == "Announcement deleted"

    def test_delete_invalid_announcement(
        self,
        client,
        mentor_token,
    ):
        res = client.delete(
            "/api/announcements/invalid-id",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 404

    def test_delete_requires_auth(
        self,
        client,
        db,
        sample_course,
    ):
        announcement = Announcement(
            course_id=sample_course.id,
            title="Delete",
            message="Delete",
        )

        db.session.add(announcement)
        db.session.commit()

        res = client.delete(
            f"/api/announcements/{announcement.id}"
        )

        assert res.status_code == 401

    def test_student_cannot_delete_announcement(
        self,
        client,
        db,
        student_token,
        sample_course,
    ):
        announcement = Announcement(
            course_id=sample_course.id,
            title="Delete",
            message="Delete",
        )

        db.session.add(announcement)
        db.session.commit()

        res = client.delete(
            f"/api/announcements/{announcement.id}",
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 403