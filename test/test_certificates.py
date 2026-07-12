from unittest.mock import patch

from app.models.certificate import Certificate


class TestCertificates:

    def test_my_certificates_empty(
        self,
        client,
        student_token,
    ):
        res = client.get(
            "/api/certificates/my",
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 200
        assert res.json == []

    def test_my_certificates_requires_auth(
        self,
        client,
    ):
        res = client.get("/api/certificates/my")

        assert res.status_code == 401

    def test_student_can_view_my_certificates(
        self,
        client,
        db,
        student_token,
        student_user,
        sample_course,
    ):
        certificate = Certificate(
            student_id=student_user.id,
            course_id=sample_course.id,
            certificate_url="certificates/test.pdf",
        )

        db.session.add(certificate)
        db.session.commit()

        res = client.get(
            "/api/certificates/my",
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 200
        assert len(res.json) == 1

    @patch("app.routes.certificate_routes.issue_certificate")
    @patch("app.routes.certificate_routes.is_course_completed")
    def test_generate_certificate(
        self,
        mock_completed,
        mock_issue,
        client,
        student_token,
        student_user,
        sample_course,
        enrolled_student,
    ):
        mock_completed.return_value = True

        certificate = Certificate(
            student_id=student_user.id,
            course_id=sample_course.id,
            certificate_url="certificates/test.pdf",
        )

        mock_issue.return_value = certificate

        res = client.post(
            f"/api/certificates/generate/{sample_course.id}",
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 201

    @patch("app.routes.certificate_routes.is_course_completed")
    def test_generate_certificate_course_not_completed(
        self,
        mock_completed,
        client,
        student_token,
        sample_course,
        enrolled_student,
    ):
        mock_completed.return_value = False

        res = client.post(
            f"/api/certificates/generate/{sample_course.id}",
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 400
        assert res.json["message"] == "Course not completed"

    def test_generate_certificate_without_enrollment(
        self,
        client,
        student_token,
        sample_course,
    ):
        res = client.post(
            f"/api/certificates/generate/{sample_course.id}",
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 403
        assert res.json["message"] == "Not enrolled in course"

    def test_generate_certificate_requires_auth(
        self,
        client,
        sample_course,
    ):
        res = client.post(
            f"/api/certificates/generate/{sample_course.id}"
        )

        assert res.status_code == 401

    def test_mentor_cannot_generate_certificate(
        self,
        client,
        mentor_token,
        sample_course,
    ):
        res = client.post(
            f"/api/certificates/generate/{sample_course.id}",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 403

    def test_get_certificate(
        self,
        client,
        db,
        student_user,
        sample_course,
    ):
        certificate = Certificate(
            student_id=student_user.id,
            course_id=sample_course.id,
            certificate_url="certificates/test.pdf",
        )

        db.session.add(certificate)
        db.session.commit()

        res = client.get(
            f"/api/certificates/{certificate.id}"
        )

        assert res.status_code == 200
        assert res.json["id"] == certificate.id

    def test_get_invalid_certificate(
        self,
        client,
    ):
        res = client.get(
            "/api/certificates/invalid-id"
        )

        assert res.status_code == 404