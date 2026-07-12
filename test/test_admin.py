import uuid
from app.models.course import Course, CourseLevel
from app.models.review import Review, ReviewStatus
from app.models.review_report import ReviewReport, ReportStatus
from app.models.user import User, UserRole


class TestAdmin:

    def test_get_all_users(self, client, admin_token):
        res = client.get('/api/admin/users', headers={
            'Authorization': f'Bearer {admin_token}'
        })
        assert res.status_code == 200

    def test_approve_course(self, client, admin_token, sample_course):
        res = client.put(
            f'/api/admin/courses/{sample_course.id}/approve',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert res.status_code == 200

    def test_reject_course(self, client, admin_token, db, mentor_user):
        from app.models.course import Course
        import uuid
        from app.models.course import CourseLevel
        course = Course(
            id=str(uuid.uuid4()),
            title="Course to Reject",
            description="Reject this",
            price=0,
            level=CourseLevel.BEGINNER,
            duration_hours=5,
            language="english",
            tags=["Test"],
            mentor_id=mentor_user.id,
            is_approved=False
        )
        db.session.add(course)
        db.session.commit()

        res = client.put(
            f'/api/admin/courses/{course.id}/reject',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert res.status_code == 200

    def test_get_admin_dashboard(self, client, admin_token):
        res = client.get('/api/admin/dashboard', headers={
            'Authorization': f'Bearer {admin_token}'
        })
        assert res.status_code == 200

    def test_admin_route_blocked_for_student(self, client, student_token):
        res = client.get('/api/admin/users', headers={
            'Authorization': f'Bearer {student_token}'
        })
        assert res.status_code == 403

    def test_change_role_to_mentor(
        self,
        client,
        admin_token,
        student_user,
    ):
        res = client.put(
            f"/api/admin/users/{student_user.id}/role",
            json={"role": "mentor"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200
        assert res.get_json()["role"] == "mentor"

    def test_change_role_to_admin(
        self,
        client,
        admin_token,
        student_user,
    ):
        res = client.put(
            f"/api/admin/users/{student_user.id}/role",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200

    def test_change_role_invalid_role(
        self,
        client,
        admin_token,
        student_user,
    ):
        res = client.put(
            f"/api/admin/users/{student_user.id}/role",
            json={"role": "random"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 400

    def test_change_role_user_not_found(
        self,
        client,
        admin_token,
    ):
        res = client.put(
            f"/api/admin/users/{uuid.uuid4()}/role",
            json={"role": "mentor"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 404

    # -------------------- COURSES --------------------

    def test_get_all_courses(
        self,
        client,
        admin_token,
    ):
        res = client.get(
            "/api/admin/courses",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200

    def test_get_all_courses_forbidden(
        self,
        client,
        student_token,
    ):
        res = client.get(
            "/api/admin/courses",
            headers={"Authorization": f"Bearer {student_token}"},
        )

        assert res.status_code == 403

    def test_approve_course_not_found(
        self,
        client,
        admin_token,
    ):
        res = client.put(
            f"/api/admin/courses/{uuid.uuid4()}/approve",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 404

    def test_reject_course_not_found(
        self,
        client,
        admin_token,
    ):
        res = client.put(
            f"/api/admin/courses/{uuid.uuid4()}/reject",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 404

    def test_delete_course(
        self,
        client,
        admin_token,
        sample_course,
    ):
        res = client.delete(
            f"/api/admin/courses/{sample_course.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200

    def test_delete_course_not_found(
        self,
        client,
        admin_token,
    ):
        res = client.delete(
            f"/api/admin/courses/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 404

    # -------------------- MENTORS --------------------

    def test_pending_mentors(
        self,
        client,
        admin_token,
        db,
    ):
        mentor = User(
            id=str(uuid.uuid4()),
            name="Pending Mentor",
            email="pending@test.com",
            role=UserRole.MENTOR,
            is_approved=False,
        )
        mentor.set_password("Test123")

        db.session.add(mentor)
        db.session.commit()

        res = client.get(
            "/api/admin/mentors/pending",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200
        assert len(res.get_json()) >= 1

    def test_approve_mentor(
        self,
        client,
        admin_token,
        db,
    ):
        mentor = User(
            id=str(uuid.uuid4()),
            name="Mentor",
            email="mentor2@test.com",
            role=UserRole.MENTOR,
            is_approved=False,
        )
        mentor.set_password("Test123")

        db.session.add(mentor)
        db.session.commit()

        res = client.put(
            f"/api/admin/mentors/{mentor.id}/approve",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200

    def test_reject_mentor(
        self,
        client,
        admin_token,
        mentor_user,
    ):
        res = client.put(
            f"/api/admin/mentors/{mentor_user.id}/reject",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200

    def test_approve_mentor_not_found(
        self,
        client,
        admin_token,
    ):
        res = client.put(
            f"/api/admin/mentors/{uuid.uuid4()}/approve",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 404

    def test_reject_mentor_not_found(
        self,
        client,
        admin_token,
    ):
        res = client.put(
            f"/api/admin/mentors/{uuid.uuid4()}/reject",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 404

    # -------------------- REVIEWS --------------------

    def test_delete_review(
        self,
        client,
        admin_token,
        db,
        enrolled_student,
        sample_course,
        student_user,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
            comment="Nice",
            status=ReviewStatus.APPROVED,
        )

        db.session.add(review)
        db.session.commit()

        res = client.delete(
            f"/api/admin/reviews/{review.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200

    def test_delete_review_not_found(
        self,
        client,
        admin_token,
    ):
        res = client.delete(
            f"/api/admin/reviews/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 404

    def test_admin_review_approve(
        self,
        client,
        admin_token,
        db,
        sample_course,
        student_user,
        enrolled_student,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=4,
            status=ReviewStatus.PENDING,
        )

        db.session.add(review)
        db.session.commit()

        res = client.put(
            f"/api/admin/reviews/{review.id}/moderate",
            json={"action": "approve"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200

    def test_admin_review_reject(
        self,
        client,
        admin_token,
        db,
        sample_course,
        student_user,
        enrolled_student,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
            status=ReviewStatus.PENDING,
        )

        db.session.add(review)
        db.session.commit()

        res = client.put(
            f"/api/admin/reviews/{review.id}/moderate",
            json={"action": "reject"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200

    def test_admin_review_invalid_action(
        self,
        client,
        admin_token,
        db,
        sample_course,
        student_user,
        enrolled_student,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
            status=ReviewStatus.PENDING,
        )

        db.session.add(review)
        db.session.commit()

        res = client.put(
            f"/api/admin/reviews/{review.id}/moderate",
            json={"action": "abc"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 400

    # -------------------- REVIEW REPORTS --------------------

    def test_get_review_reports(
        self,
        client,
        admin_token,
        db,
        sample_course,
        student_user,
        enrolled_student,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
        )

        db.session.add(review)
        db.session.commit()

        report = ReviewReport(
            review_id=review.id,
            reporter_id=student_user.id,
            reason="Spam",
            status=ReportStatus.PENDING,
        )

        db.session.add(report)
        db.session.commit()

        res = client.get(
            "/api/admin/review-reports",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200

    def test_resolve_review_report(
        self,
        client,
        admin_token,
        db,
        sample_course,
        student_user,
        enrolled_student,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
        )

        db.session.add(review)
        db.session.commit()

        report = ReviewReport(
            review_id=review.id,
            reporter_id=student_user.id,
            reason="Spam",
            status=ReportStatus.PENDING,
        )

        db.session.add(report)
        db.session.commit()

        res = client.put(
            f"/api/admin/review-reports/{report.id}",
            json={"action": "resolve"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200

    def test_dismiss_review_report(
        self,
        client,
        admin_token,
        db,
        sample_course,
        student_user,
        enrolled_student,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
        )

        db.session.add(review)
        db.session.commit()

        report = ReviewReport(
            review_id=review.id,
            reporter_id=student_user.id,
            reason="Spam",
            status=ReportStatus.PENDING,
        )

        db.session.add(report)
        db.session.commit()

        res = client.put(
            f"/api/admin/review-reports/{report.id}",
            json={"action": "dismiss"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 200

    def test_review_report_invalid_action(
        self,
        client,
        admin_token,
        db,
        sample_course,
        student_user,
        enrolled_student,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=student_user.id,
            rating=5,
        )

        db.session.add(review)
        db.session.commit()

        report = ReviewReport(
            review_id=review.id,
            reporter_id=student_user.id,
            reason="Spam",
            status=ReportStatus.PENDING,
        )

        db.session.add(report)
        db.session.commit()

        res = client.put(
            f"/api/admin/review-reports/{report.id}",
            json={"action": "wrong"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 400

    def test_review_report_not_found(
        self,
        client,
        admin_token,
    ):
        res = client.put(
            f"/api/admin/review-reports/{uuid.uuid4()}",
            json={"action": "resolve"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert res.status_code == 404