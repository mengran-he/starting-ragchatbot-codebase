"""API endpoint tests for the RAG chatbot FastAPI application.

Uses the test app and fixtures defined in conftest.py to avoid importing the
production app.py (which mounts static files that don't exist in CI/test
environments).
"""
import pytest
from unittest.mock import MagicMock
from helpers import build_test_app
from fastapi.testclient import TestClient


# ===========================================================================
# POST /api/query
# ===========================================================================

class TestQueryEndpoint:
    """Tests for POST /api/query."""

    def test_returns_answer_and_sources(self, client, sample_query_payload):
        response = client.post("/api/query", json=sample_query_payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data

    def test_answer_text_matches_mock(self, client, sample_query_payload):
        response = client.post("/api/query", json=sample_query_payload)
        assert response.json()["answer"] == "Python is a high-level programming language."

    def test_sources_contain_text_and_link(self, client, sample_query_payload):
        response = client.post("/api/query", json=sample_query_payload)
        sources = response.json()["sources"]
        assert len(sources) == 1
        assert sources[0]["text"] == "Intro to Python - Lesson 1"
        assert sources[0]["link"] == "https://example.com/lesson1"

    def test_auto_creates_session_when_none_provided(self, client, mock_rag, sample_query_payload):
        response = client.post("/api/query", json=sample_query_payload)
        assert response.status_code == 200
        assert response.json()["session_id"] == "test-session-abc"
        mock_rag.session_manager.create_session.assert_called_once()

    def test_uses_provided_session_id(self, client, mock_rag, sample_query_payload_with_session):
        response = client.post("/api/query", json=sample_query_payload_with_session)
        assert response.status_code == 200
        assert response.json()["session_id"] == "existing-session-xyz"
        # create_session should NOT be called when a session_id is supplied
        mock_rag.session_manager.create_session.assert_not_called()

    def test_rag_query_called_with_correct_args(self, client, mock_rag, sample_query_payload_with_session):
        client.post("/api/query", json=sample_query_payload_with_session)
        mock_rag.query.assert_called_once_with("Tell me more", "existing-session-xyz")

    def test_missing_query_field_returns_422(self, client):
        response = client.post("/api/query", json={})
        assert response.status_code == 422

    def test_rag_exception_returns_500(self, mock_rag):
        mock_rag.query.side_effect = RuntimeError("DB is down")
        app = build_test_app(mock_rag)
        error_client = TestClient(app, raise_server_exceptions=False)
        response = error_client.post("/api/query", json={"query": "test"})
        assert response.status_code == 500
        assert "DB is down" in response.json()["detail"]

    def test_plain_string_sources_are_handled(self, mock_rag):
        """Backward-compat: sources returned as plain strings (not dicts)."""
        mock_rag.query.return_value = ("answer", ["Course A - Lesson 2"])
        app = build_test_app(mock_rag)
        str_client = TestClient(app)
        response = str_client.post("/api/query", json={"query": "hello"})
        assert response.status_code == 200
        sources = response.json()["sources"]
        assert sources[0]["text"] == "Course A - Lesson 2"
        assert sources[0]["link"] is None

    def test_empty_sources_list(self, mock_rag):
        mock_rag.query.return_value = ("answer with no sources", [])
        app = build_test_app(mock_rag)
        no_src_client = TestClient(app)
        response = no_src_client.post("/api/query", json={"query": "hello"})
        assert response.status_code == 200
        assert response.json()["sources"] == []


# ===========================================================================
# GET /api/courses
# ===========================================================================

class TestCoursesEndpoint:
    """Tests for GET /api/courses."""

    def test_returns_total_courses_and_titles(self, client):
        response = client.get("/api/courses")
        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 2
        assert data["course_titles"] == ["Intro to Python", "Advanced Python"]

    def test_analytics_called_once(self, client, mock_rag):
        client.get("/api/courses")
        mock_rag.get_course_analytics.assert_called_once()

    def test_rag_exception_returns_500(self, mock_rag):
        mock_rag.get_course_analytics.side_effect = RuntimeError("Analytics failed")
        app = build_test_app(mock_rag)
        error_client = TestClient(app, raise_server_exceptions=False)
        response = error_client.get("/api/courses")
        assert response.status_code == 500
        assert "Analytics failed" in response.json()["detail"]

    def test_empty_catalog(self, mock_rag):
        mock_rag.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": [],
        }
        app = build_test_app(mock_rag)
        empty_client = TestClient(app)
        response = empty_client.get("/api/courses")
        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []


# ===========================================================================
# DELETE /api/session/{session_id}
# ===========================================================================

class TestDeleteSessionEndpoint:
    """Tests for DELETE /api/session/{session_id}."""

    def test_returns_ok_status(self, client):
        response = client.delete("/api/session/some-session-id")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_delete_called_with_correct_session_id(self, client, mock_rag):
        client.delete("/api/session/my-session-123")
        mock_rag.session_manager.delete_session.assert_called_once_with("my-session-123")
