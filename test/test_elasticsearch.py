import pytest
from unittest.mock import MagicMock, patch

from app.services.elasticsearch_service import (
    ensure_indices,
    index_course,
    index_mentor,
    delete_course_from_index,
    reindex_all,
    search_courses,
    search_mentors,
    autocomplete,
    _build_filters,
    _course_document,
    _mentor_document,
)


class TestElasticSearchService:

    # -----------------------------
    # ensure_indices
    # -----------------------------

    @patch("app.services.elasticsearch_service._client")
    def test_ensure_indices_no_client(self, mock_client):
        mock_client.return_value = None

        assert ensure_indices() is False

    @patch("app.services.elasticsearch_service._client")
    def test_ensure_indices_creates_missing_indices(self, mock_client):
        es = MagicMock()

        es.indices.exists.return_value = False
        mock_client.return_value = es

        assert ensure_indices() is True
        assert es.indices.create.call_count == 2

    @patch("app.services.elasticsearch_service._client")
    def test_ensure_indices_existing_indices(self, mock_client):
        es = MagicMock()

        es.indices.exists.return_value = True
        mock_client.return_value = es

        assert ensure_indices() is True
        es.indices.create.assert_not_called()

    # -----------------------------
    # _build_filters
    # -----------------------------

    def test_build_filters_empty(self):
        filters = _build_filters({})

        assert {"term": {"is_approved": True}} in filters

    def test_build_filters_price(self):
        filters = _build_filters({
            "min_price": 100,
            "max_price": 500
        })

        assert any("price" in str(f) for f in filters)

    def test_build_filters_level(self):
        filters = _build_filters({
            "level": "beginner"
        })

        assert {"term": {"level": "beginner"}} in filters

    def test_build_filters_duration(self):
        filters = _build_filters({
            "min_duration": 5,
            "max_duration": 10
        })

        assert any("duration_hours" in str(f) for f in filters)

    def test_build_filters_language(self):
        filters = _build_filters({
            "language": "english"
        })

        assert {"term": {"language": "english"}} in filters

    def test_build_filters_rating(self):
        filters = _build_filters({
            "min_rating": 4
        })

        assert any("rating" in str(f) for f in filters)

    def test_build_filters_tags(self):
        filters = _build_filters({
            "tags": "python,flask"
        })

        matches = [
            f for f in filters if "match" in f
        ]

        assert len(matches) == 2

    # -----------------------------
    # course document
    # -----------------------------

    @patch("app.services.elasticsearch_service.calculate_weighted_rating")
    def test_course_document(
        self,
        mock_rating,
        sample_course,
    ):
        mock_rating.return_value = 4.5

        doc = _course_document(sample_course)

        assert doc["id"] == sample_course.id
        assert doc["title"] == sample_course.title
        assert doc["rating"] == 4.5
        assert "suggest" in doc

    # -----------------------------
    # mentor document
    # -----------------------------

    def test_mentor_document(self, mentor_user):
        doc = _mentor_document(mentor_user)

        assert doc["id"] == mentor_user.id
        assert doc["name"] == mentor_user.name
        assert "suggest" in doc

    # -----------------------------
    # index_course
    # -----------------------------

    @patch("app.services.elasticsearch_service.ensure_indices")
    @patch("app.services.elasticsearch_service._client")
    def test_index_course_success(
        self,
        mock_client,
        mock_indices,
        sample_course,
    ):
        es = MagicMock()

        mock_client.return_value = es
        mock_indices.return_value = True

        assert index_course(sample_course) is True

        es.index.assert_called()

    @patch("app.services.elasticsearch_service._client")
    def test_index_course_no_client(
        self,
        mock_client,
        sample_course,
    ):
        mock_client.return_value = None

        assert index_course(sample_course) is False

    # -----------------------------
    # index_mentor
    # -----------------------------

    @patch("app.services.elasticsearch_service.ensure_indices")
    @patch("app.services.elasticsearch_service._client")
    def test_index_mentor_success(
        self,
        mock_client,
        mock_indices,
        mentor_user,
    ):
        es = MagicMock()

        mock_client.return_value = es
        mock_indices.return_value = True

        assert index_mentor(mentor_user) is True

    @patch("app.services.elasticsearch_service._client")
    def test_index_mentor_no_client(
        self,
        mock_client,
        mentor_user,
    ):
        mock_client.return_value = None

        assert index_mentor(mentor_user) is False

    # -----------------------------
    # delete
    # -----------------------------

    @patch("app.services.elasticsearch_service._client")
    def test_delete_course_success(
        self,
        mock_client,
        sample_course,
    ):
        es = MagicMock()

        es.indices.exists.return_value = True

        mock_client.return_value = es

        assert delete_course_from_index(sample_course.id)

        es.delete.assert_called_once()

    @patch("app.services.elasticsearch_service._client")
    def test_delete_course_no_client(
        self,
        mock_client,
        sample_course,
    ):
        mock_client.return_value = None

        assert delete_course_from_index(sample_course.id) is False

    # -----------------------------
    # reindex
    # -----------------------------

    @patch("app.services.elasticsearch_service.ensure_indices")
    def test_reindex_unavailable(
        self,
        mock_indices,
    ):
        mock_indices.return_value = False

        result = reindex_all()

        assert result["status"] == "unavailable"

    @patch("app.services.elasticsearch_service.index_course")
    @patch("app.services.elasticsearch_service.index_mentor")
    @patch("app.services.elasticsearch_service.ensure_indices")
    def test_reindex_success(
        self,
        mock_indices,
        mock_index_mentor,
        mock_index_course,
    ):
        mock_indices.return_value = True

        result = reindex_all()

        assert result["status"] == "ok"

    # -----------------------------
    # search
    # -----------------------------

    @patch("app.services.elasticsearch_service.ensure_indices")
    @patch("app.services.elasticsearch_service._client")
    @patch("app.services.elasticsearch_service._sql_search_courses")
    def test_search_courses_database_fallback(
        self,
        mock_sql,
        mock_client,
        mock_indices,
    ):
        mock_client.return_value = None

        mock_sql.return_value = {
            "courses": [],
            "engine": "database"
        }

        result = search_courses({})

        assert result["engine"] == "database"

    @patch("app.services.elasticsearch_service.ensure_indices")
    @patch("app.services.elasticsearch_service._client")
    @patch("app.services.elasticsearch_service._sql_search_mentors")
    def test_search_mentors_database_fallback(
        self,
        mock_sql,
        mock_client,
        mock_indices,
    ):
        mock_client.return_value = None

        mock_sql.return_value = {
            "mentors": [],
            "engine": "database"
        }

        result = search_mentors({})

        assert result["engine"] == "database"

    # -----------------------------
    # autocomplete
    # -----------------------------

    @patch("app.services.elasticsearch_service._client")
    def test_autocomplete_empty_prefix(self, mock_client):
        result = autocomplete("")

        assert result["suggestions"] == []

    @patch("app.services.elasticsearch_service.ensure_indices")
    @patch("app.services.elasticsearch_service._client")
    def test_autocomplete_no_client(
        self,
        mock_client,
        mock_indices,
    ):
        mock_client.return_value = None

        result = autocomplete("python")

        assert result["suggestions"] == []