import uuid
from unittest.mock import patch

from app.extensions import db
from app.models.user import User, UserRole
from app.models.review import Review, ReviewStatus
from app.models.review_report import ReviewReport, ReportStatus
from app.models.enrollment import Enrollment

class TestReviews:

    def test_post_review(self, client, student_token,
                          enrolled_student, sample_course):
        res = client.post(
            f'/api/reviews/{sample_course.id}',
            json={'rating': 5, 'comment': 'Excellent course!'},
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 201

    def test_post_duplicate_review_fails(self, client, student_token,
                                          enrolled_student, sample_course):
        client.post(
            f'/api/reviews/{sample_course.id}',
            json={'rating': 4, 'comment': 'Good'},
            headers={'Authorization': f'Bearer {student_token}'}
        )
        res = client.post(
            f'/api/reviews/{sample_course.id}',
            json={'rating': 3, 'comment': 'Second review'},
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 400

    def test_get_course_reviews(self, client, sample_course):
        res = client.get(f'/api/reviews/{sample_course.id}')
        assert res.status_code == 200

    def test_review_requires_enrollment(self, client, student_token):
        import uuid
        fake_id = str(uuid.uuid4())
        res = client.post(
            f'/api/reviews/{fake_id}',
            json={'rating': 5, 'comment': 'Test'},
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code in [403, 404]

    def create_second_student(self, client):
        student = User(
            id=str(uuid.uuid4()),
            name="Student Two",
            email="student2@test.com",
            role=UserRole.STUDENT,
            is_approved=True,
        )
        student.set_password("Test@1234")
        db.session.add(student)
        db.session.commit()

        db.session.add(
            Enrollment(
                id=str(uuid.uuid4()),
                student_id=student.id,
                course_id=self.course.id,
            )
        )
        db.session.commit()

        token = client.post(
            "/api/auth/login",
            json={
                "email": "student2@test.com",
                "password": "Test@1234",
            },
        ).get_json()["access_token"]

        return student, token

    def setup_review(
        self,
        student_user,
        sample_course,
    ):
        self.course = sample_course

        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
            comment="Excellent",
            status=ReviewStatus.APPROVED,
        )

        db.session.add(review)
        db.session.commit()

        return review

    ##############################################################
    # CREATE REVIEW
    ##############################################################

    def test_review_invalid_rating_low(
        self,
        client,
        student_token,
        enrolled_student,
        sample_course,
    ):
        res = client.post(
            f"/api/reviews/{sample_course.id}",
            json={
                "rating": 0,
                "comment": "Bad",
            },
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 400

    def test_review_invalid_rating_high(
        self,
        client,
        student_token,
        enrolled_student,
        sample_course,
    ):
        res = client.post(
            f"/api/reviews/{sample_course.id}",
            json={
                "rating": 6,
                "comment": "Bad",
            },
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 400

    def test_review_without_rating(
        self,
        client,
        student_token,
        enrolled_student,
        sample_course,
    ):
        res = client.post(
            f"/api/reviews/{sample_course.id}",
            json={
                "comment": "Missing rating"
            },
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 400

    def test_review_requires_login(
        self,
        client,
        sample_course,
    ):
        res = client.post(
            f"/api/reviews/{sample_course.id}",
            json={
                "rating": 5
            },
        )

        assert res.status_code == 401

    ##############################################################
    # GET REVIEWS
    ##############################################################

    def test_rejected_reviews_hidden(
        self,
        client,
        student_user,
        sample_course,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
            comment="Hidden",
            status=ReviewStatus.REJECTED,
        )

        db.session.add(review)
        db.session.commit()

        res = client.get(
            f"/api/reviews/{sample_course.id}"
        )

        data = res.get_json()

        assert data["total"] == 0

    ##############################################################
    # REPORT REVIEW
    ##############################################################

    def test_report_review_success(
        self,
        client,
        student_user,
        student_token,
        sample_course,
    ):
        self.course = sample_course

        review = self.setup_review(
            student_user,
            sample_course,
        )

        _, second_token = self.create_second_student(client)

        res = client.post(
            f"/api/reviews/{review.id}/report",
            json={
                "reason": "Spam"
            },
            headers={
                "Authorization": f"Bearer {second_token}"
            },
        )

        assert res.status_code == 201

    def test_report_nonexistent_review(
        self,
        client,
        student_token,
    ):
        res = client.post(
            f"/api/reviews/{uuid.uuid4()}/report",
            json={
                "reason": "Spam"
            },
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 404

    def test_report_own_review_forbidden(
        self,
        client,
        student_user,
        student_token,
        sample_course,
    ):
        review = self.setup_review(
            student_user,
            sample_course,
        )

        res = client.post(
            f"/api/reviews/{review.id}/report",
            json={
                "reason": "Spam"
            },
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 400

    def test_report_without_reason(
        self,
        client,
        student_user,
        sample_course,
    ):
        self.course = sample_course

        review = self.setup_review(
            student_user,
            sample_course,
        )

        _, second_token = self.create_second_student(client)

        res = client.post(
            f"/api/reviews/{review.id}/report",
            json={},
            headers={
                "Authorization": f"Bearer {second_token}"
            },
        )

        assert res.status_code == 400

    def test_duplicate_report(
        self,
        client,
        student_user,
        sample_course,
    ):
        self.course = sample_course

        review = self.setup_review(
            student_user,
            sample_course,
        )

        second_student, second_token = self.create_second_student(client)

        report = ReviewReport(
            review_id=review.id,
            reporter_id=second_student.id,
            reason="Spam",
            status=ReportStatus.PENDING,
        )

        db.session.add(report)
        db.session.commit()

        res = client.post(
            f"/api/reviews/{review.id}/report",
            json={
                "reason": "Again"
            },
            headers={
                "Authorization": f"Bearer {second_token}"
            },
        )

        assert res.status_code == 400

    ##############################################################
    # MODERATE REVIEW
    ##############################################################

    @patch("app.routes.review_routes.index_course")
    def test_admin_approve_review(
        self,
        mock_index,
        client,
        admin_token,
        student_user,
        sample_course,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
            comment="Good",
            status=ReviewStatus.PENDING,
        )

        db.session.add(review)
        db.session.commit()

        res = client.put(
            f"/api/reviews/{review.id}/moderate",
            json={
                "action": "approve"
            },
            headers={
                "Authorization": f"Bearer {admin_token}"
            },
        )

        assert res.status_code == 200

    @patch("app.routes.review_routes.index_course")
    def test_mentor_reject_review(
        self,
        mock_index,
        client,
        mentor_token,
        student_user,
        sample_course,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=4,
            comment="Average",
            status=ReviewStatus.PENDING,
        )

        db.session.add(review)
        db.session.commit()

        res = client.put(
            f"/api/reviews/{review.id}/moderate",
            json={
                "action": "reject"
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 200

    def test_moderate_invalid_action(
        self,
        client,
        mentor_token,
        student_user,
        sample_course,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
            comment="Test",
            status=ReviewStatus.PENDING,
        )

        db.session.add(review)
        db.session.commit()

        res = client.put(
            f"/api/reviews/{review.id}/moderate",
            json={
                "action": "delete"
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 400

    def test_moderate_nonexistent_review(
        self,
        client,
        mentor_token,
    ):
        res = client.put(
            f"/api/reviews/{uuid.uuid4()}/moderate",
            json={
                "action": "approve"
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 404

    def test_student_cannot_moderate(
        self,
        client,
        student_token,
        student_user,
        sample_course,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
            comment="Good",
            status=ReviewStatus.PENDING,
        )

        db.session.add(review)
        db.session.commit()

        res = client.put(
            f"/api/reviews/{review.id}/moderate",
            json={
                "action": "approve"
            },
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 403

    ##############################################################
    # PENDING REVIEWS
    ##############################################################

    def test_pending_reviews(
        self,
        client,
        mentor_token,
        student_user,
        sample_course,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
            comment="Pending",
            status=ReviewStatus.PENDING,
        )

        db.session.add(review)
        db.session.commit()

        res = client.get(
            f"/api/reviews/pending/{sample_course.id}",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 200
        assert len(res.get_json()) == 1

    def test_pending_reviews_course_not_found(
        self,
        client,
        mentor_token,
    ):
        res = client.get(
            f"/api/reviews/pending/{uuid.uuid4()}",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 404

    def test_student_cannot_view_pending(
        self,
        client,
        student_token,
        sample_course,
    ):
        res = client.get(
            f"/api/reviews/pending/{sample_course.id}",
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 403