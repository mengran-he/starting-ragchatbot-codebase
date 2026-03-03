"""Shared fixtures for the RAG chatbot test suite."""
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from helpers import build_test_app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_rag():
    """Mock RAGSystem with sensible defaults."""
    rag = MagicMock()
    rag.session_manager.create_session.return_value = "test-session-abc"
    rag.query.return_value = (
        "Python is a high-level programming language.",
        [{"text": "Intro to Python - Lesson 1", "link": "https://example.com/lesson1"}],
    )
    rag.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Intro to Python", "Advanced Python"],
    }
    return rag


@pytest.fixture
def client(mock_rag):
    """TestClient wired to the test app with the default mock RAG."""
    app = build_test_app(mock_rag)
    return TestClient(app)


@pytest.fixture
def sample_query_payload():
    """A valid /api/query request body."""
    return {"query": "What is Python?"}


@pytest.fixture
def sample_query_payload_with_session():
    """A valid /api/query request body that includes an existing session ID."""
    return {"query": "Tell me more", "session_id": "existing-session-xyz"}
