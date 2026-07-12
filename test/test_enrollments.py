from app.extensions import db

class TestEnrollments:

    def test_enroll_in_free_course(
        self,
        client,
        student_token,
        sample_course
    ):
        sample_course.price = 0
        db.session.commit()

        res = client.post(
            f"/api/enrollments/{sample_course.id}",
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code in [200, 201]

    def test_get_my_enrolled_courses(self, client, student_token,
                                      enrolled_student):
        res = client.get('/api/enrollments/my-courses', headers={
            'Authorization': f'Bearer {student_token}'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert isinstance(data, list)

    def test_enroll_without_auth_fails(self, client, sample_course):
        res = client.post(f'/api/enrollments/{sample_course.id}')
        assert res.status_code == 401