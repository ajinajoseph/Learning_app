from app.extensions import db
from app.models.review import Review, ReviewStatus
from app.models.progress import Progress
from app.models.user import User
from app.models.user import UserRole
from flask_jwt_extended import create_access_token
import uuid

class TestAnalytics:

    def test_course_analytics(
        self,
        client,
        mentor_token,
        sample_course,
        sample_module,
        sample_lesson,
        enrolled_student,
    ):
        review = Review(
            course_id=sample_course.id,
            student_id=enrolled_student.student_id,
            rating=5,
            comment="Excellent",
            status=ReviewStatus.APPROVED,
        )

        progress = Progress(
            student_id=enrolled_student.student_id,
            lesson_id=sample_lesson.id,
            completed=True,
        )

        db.session.add(review)
        db.session.add(progress)
        db.session.commit()

        res = client.get(
            f"/api/analytics/course/{sample_course.id}",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 200

        data = res.get_json()

        assert data["course_id"] == sample_course.id
        assert data["total_students"] == 1
        assert data["total_reviews"] == 1
        assert data["average_rating"] == 5
        assert data["completion_rate"] == 100.0

    def test_course_analytics_course_not_found(
        self,
        client,
        mentor_token,
    ):
        res = client.get(
            "/api/analytics/course/invalid-id",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 404
        assert res.get_json()["message"] == "Course not found"

    def test_course_analytics_student_forbidden(
        self,
        client,
        student_token,
        sample_course,
    ):
        res = client.get(
            f"/api/analytics/course/{sample_course.id}",
            headers={
                "Authorization": f"Bearer {student_token}"
            },
        )

        assert res.status_code == 403


    def test_course_analytics_other_mentor_forbidden(
    self,
    client,
    app,
    sample_course,
    other_mentor,
    ):
        with app.app_context():
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=other_mentor.id)

        res = client.get(
            f"/api/analytics/course/{sample_course.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert res.status_code == 403
        assert res.get_json()["message"] == "Access denied"
    def test_course_analytics_no_reviews(
        self,
        client,
        mentor_token,
        sample_course,
        enrolled_student,
    ):
        res = client.get(
            f"/api/analytics/course/{sample_course.id}",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 200

        data = res.get_json()

        assert data["total_reviews"] == 0
        assert data["completion_rate"] == 0

    def test_course_analytics_no_students(
        self,
        client,
        mentor_token,
        sample_course,
    ):
        res = client.get(
            f"/api/analytics/course/{sample_course.id}",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
        )

        assert res.status_code == 200

        data = res.get_json()

        assert data["total_students"] == 0
        assert data["completion_rate"] == 0

    def test_course_analytics_requires_auth(
        self,
        client,
        sample_course,
    ):
        res = client.get(
            f"/api/analytics/course/{sample_course.id}"
        )

        assert res.status_code == 401