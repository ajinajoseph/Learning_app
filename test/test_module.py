class TestModules:

    def test_create_module(
        self,
        client,
        mentor_token,
        sample_course
    ):
        res = client.post(
            "/api/modules",
            json={
                "title": "Module 1",
                "description": "Basics",
                "course_id": sample_course.id
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 201
        data = res.get_json()
        assert data["title"] == "Module 1"


    def test_create_module_invalid_course(
        self,
        client,
        mentor_token
    ):
        res = client.post(
            "/api/modules",
            json={
                "title": "Module",
                "course_id": "invalid-id"
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 404


    def test_create_module_requires_auth(
        self,
        client,
        sample_course
    ):
        res = client.post(
            "/api/modules",
            json={
                "title": "Module",
                "course_id": sample_course.id
            }
        )

        assert res.status_code == 401


    def test_student_cannot_create_module(
        self,
        client,
        student_token,
        sample_course
    ):
        res = client.post(
            "/api/modules",
            json={
                "title": "Module",
                "course_id": sample_course.id
            },
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 403


    def test_get_modules(
        self,
        client,
        sample_course,
        sample_module
    ):
        res = client.get(
            f"/api/modules/course/{sample_course.id}"
        )

        assert res.status_code == 200
        assert isinstance(res.get_json(), list)


    def test_get_modules_empty(
        self,
        client,
        sample_course
    ):
        res = client.get(
            f"/api/modules/course/{sample_course.id}"
        )

        assert res.status_code == 200


    def test_get_module(
        self,
        client,
        sample_module
    ):
        res = client.get(
            f"/api/modules/{sample_module.id}"
        )

        assert res.status_code == 200

        data = res.get_json()
        assert data["id"] == sample_module.id


    def test_get_invalid_module(
        self,
        client
    ):
        res = client.get(
            "/api/modules/invalid-id"
        )

        assert res.status_code == 404


    def test_update_module(
        self,
        client,
        mentor_token,
        sample_module
    ):
        res = client.put(
            f"/api/modules/{sample_module.id}",
            json={
                "title": "Updated Module",
                "description": "Updated"
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 200

        data = res.get_json()
        assert data["title"] == "Updated Module"


    def test_update_invalid_module(
        self,
        client,
        mentor_token
    ):
        res = client.put(
            "/api/modules/invalid-id",
            json={
                "title": "ABC"
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 404


    def test_update_requires_auth(
        self,
        client,
        sample_module
    ):
        res = client.put(
            f"/api/modules/{sample_module.id}",
            json={
                "title": "ABC"
            }
        )

        assert res.status_code == 401


    def test_student_cannot_update_module(
        self,
        client,
        student_token,
        sample_module
    ):
        res = client.put(
            f"/api/modules/{sample_module.id}",
            json={
                "title": "Hack"
            },
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 403


    def test_delete_module(
        self,
        client,
        mentor_token,
        sample_module
    ):
        res = client.delete(
            f"/api/modules/{sample_module.id}",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 200


    def test_delete_invalid_module(
        self,
        client,
        mentor_token
    ):
        res = client.delete(
            "/api/modules/invalid-id",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 404


    def test_delete_requires_auth(
        self,
        client,
        sample_module
    ):
        res = client.delete(
            f"/api/modules/{sample_module.id}"
        )

        assert res.status_code == 401


    def test_student_cannot_delete_module(
        self,
        client,
        student_token,
        sample_module
    ):
        res = client.delete(
            f"/api/modules/{sample_module.id}",
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 403