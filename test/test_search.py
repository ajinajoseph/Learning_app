from unittest.mock import patch


class TestSearchRoutes:

    def test_search_courses(self, client):
        with patch(
            "app.routes.search_routes.search_courses"
        ) as mock_search:

            mock_search.return_value = {
                "courses": [],
                "total": 0,
                "engine": "database",
            }

            res = client.get("/api/search/courses?q=python")

            assert res.status_code == 200
            assert res.get_json()["engine"] == "database"

    def test_search_courses_with_filters(self, client):
        with patch(
            "app.routes.search_routes.search_courses"
        ) as mock_search:

            mock_search.return_value = {
                "courses": [],
                "total": 0,
                "engine": "database",
            }

            res = client.get(
                "/api/search/courses?"
                "q=python"
                "&min_price=100"
                "&max_price=500"
                "&level=beginner"
                "&language=english"
            )

            assert res.status_code == 200

    def test_search_mentors(self, client):
        with patch(
            "app.routes.search_routes.search_mentors"
        ) as mock_search:

            mock_search.return_value = {
                "mentors": [],
                "total": 0,
                "engine": "database",
            }

            res = client.get("/api/search/mentors?q=john")

            assert res.status_code == 200
            assert "mentors" in res.get_json()

    def test_autocomplete(self, client):
        with patch(
            "app.routes.search_routes.autocomplete"
        ) as mock_auto:

            mock_auto.return_value = {
                "suggestions": [
                    {
                        "text": "Python",
                        "type": "course",
                    }
                ]
            }

            res = client.get("/api/search/autocomplete?q=py")

            assert res.status_code == 200
            assert len(res.get_json()["suggestions"]) == 1

    def test_autocomplete_empty_query(self, client):
        with patch(
            "app.routes.search_routes.autocomplete"
        ) as mock_auto:

            mock_auto.return_value = {
                "suggestions": []
            }

            res = client.get("/api/search/autocomplete")

            assert res.status_code == 200
            assert res.get_json()["suggestions"] == []

    def test_reindex_success(
        self,
        client,
        admin_token,
    ):
        with patch(
            "app.routes.search_routes.reindex_all"
        ) as mock_reindex:

            mock_reindex.return_value = {
                "status": "ok",
                "courses": 10,
                "mentors": 3,
            }

            res = client.post(
                "/api/search/reindex",
                headers={
                    "Authorization":
                    f"Bearer {admin_token}"
                },
            )

            assert res.status_code == 200
            assert res.get_json()["status"] == "ok"

    def test_reindex_service_unavailable(
        self,
        client,
        admin_token,
    ):
        with patch(
            "app.routes.search_routes.reindex_all"
        ) as mock_reindex:

            mock_reindex.return_value = {
                "status": "unavailable",
                "courses": 0,
                "mentors": 0,
            }

            res = client.post(
                "/api/search/reindex",
                headers={
                    "Authorization":
                    f"Bearer {admin_token}"
                },
            )

            assert res.status_code == 503

    def test_reindex_requires_login(
        self,
        client,
    ):
        res = client.post("/api/search/reindex")

        assert res.status_code == 401

    def test_reindex_student_forbidden(
        self,
        client,
        student_token,
    ):
        res = client.post(
            "/api/search/reindex",
            headers={
                "Authorization":
                f"Bearer {student_token}"
            },
        )

        assert res.status_code == 403