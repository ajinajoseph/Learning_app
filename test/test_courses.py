from test.conftest import sample_course


class TestCourses:
    def test_create_course_as_mentor(self, client, mentor_token):
        res = client.post('/api/courses', json={
            'title': 'New Test Course',
            'description': 'A brand new course',
            'price': 499.0,
            'level': 'beginner',    # API accepts string, backend converts
            'language': 'English',

        }, headers={'Authorization': f'Bearer {mentor_token}'})
        assert res.status_code == 201

    def test_create_course_as_student_fails(self, client, student_token):
        res = client.post('/api/courses', json={
            'title': 'Student Course',
            'description': 'Should fail',
            'price': 0,
            'level': 'beginner',
            'language': 'English',
        }, headers={'Authorization': f'Bearer {student_token}'})
        assert res.status_code == 403
    def test_get_courses(self,client):
        res = client.get("/api/courses")
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)
    def test_get_course_by_id(self, client, sample_course):
        res = client.get(f"/api/courses/{sample_course.id}")

        assert res.status_code == 200
        assert res.get_json()["id"] == sample_course.id
    def test_get_invalid_course(self, client):
        res = client.get("/api/courses/999999")
        assert res.status_code == 404
    def test_create_course_invalid_level(self, client, mentor_token):
        res = client.post(
            "/api/courses",
            json={
                "title":"Python",
                "description":"Test",
                "price":100,
                "level":"expert123"
            },
            headers={"Authorization":f"Bearer {mentor_token}"}
        )
        assert res.status_code == 400
    def test_my_courses(self, client, mentor_token):
        res = client.get(
            "/api/courses/my-courses",
            headers={"Authorization":f"Bearer {mentor_token}"}
        )

        assert res.status_code == 200
        assert isinstance(res.json, list)

    def test_my_courses_without_login(self, client):
        res = client.get("/api/courses/my-courses")

        assert res.status_code == 401
    def test_search_courses(self, client):
        res = client.get("/api/courses/search?q=python")
        assert res.status_code == 200
    def test_paginated_courses(self, client):
        res = client.get("/api/courses/paginated")

        assert res.status_code == 200

        assert "courses" in res.json
        assert "pages" in res.json
    def test_update_course(self, client, mentor_token, sample_course):
        res = client.put(
            f"/api/courses/{sample_course.id}",
            json={
                "title":"Updated Title"
            },
            headers={"Authorization":f"Bearer {mentor_token}"}
        )

        assert res.status_code == 200
        assert res.json["course"]["title"] == "Updated Title"
    def test_update_invalid_course(self, client, mentor_token):
        res = client.put(
            "/api/courses/999999",
            json={"title":"Test"},
            headers={"Authorization":f"Bearer {mentor_token}"}
        )

        assert res.status_code == 404
    def test_student_cannot_update_course(
    self,
    client,
    student_token,
    sample_course
):
        res = client.put(
            f"/api/courses/{sample_course.id}",
            json={"title":"Hack"},
            headers={"Authorization":f"Bearer {student_token}"}
        )

        assert res.status_code == 403
    def test_update_invalid_level(
    self,
    client,
    mentor_token,
    sample_course
):
        res = client.put(
            f"/api/courses/{sample_course.id}",
            json={
                "level":"wronglevel"
            },
            headers={"Authorization":f"Bearer {mentor_token}"}
        )

        assert res.status_code == 400
    def test_delete_course(
    self,
    client,
    mentor_token,
    sample_course
):
        res = client.delete(
            f"/api/courses/{sample_course.id}",
            headers={"Authorization":f"Bearer {mentor_token}"}
        )

        assert res.status_code == 200
    def test_delete_invalid_course(
    self,
    client,
    mentor_token
):
        res = client.delete(
            "/api/courses/999999",
            headers={"Authorization":f"Bearer {mentor_token}"}
        )

        assert res.status_code == 404

    def test_student_cannot_delete_course(
    self,
    client,
    student_token,
    sample_course
    ):
        res = client.delete(
            f"/api/courses/{sample_course.id}",
            headers={"Authorization":f"Bearer {student_token}"}
        )

        assert res.status_code == 403

    def test_course_content_without_enrollment(
    self,
    client,
    student_token,
    sample_course
):
        res = client.get(
            f"/api/courses/{sample_course.id}/content",
            headers={"Authorization":f"Bearer {student_token}"}
        )

        assert res.status_code == 403

    def test_course_content_as_mentor(
    self,
    client,
    mentor_token,
    sample_course
):
        res = client.get(
            f"/api/courses/{sample_course.id}/content",
            headers={"Authorization":f"Bearer {mentor_token}"}
        )

        assert res.status_code == 200

    def test_get_enrolled_students(
    self,
    client,
    mentor_token,
    sample_course
):
        res = client.get(
            f"/api/courses/{sample_course.id}/students",
            headers={"Authorization":f"Bearer {mentor_token}"}
        )

        assert res.status_code == 200
    def test_student_cannot_view_students(
    self,
    client,
    student_token,
    sample_course
):
        res = client.get(
            f"/api/courses/{sample_course.id}/students",
            headers={"Authorization":f"Bearer {student_token}"}
        )

        assert res.status_code == 403
    
        