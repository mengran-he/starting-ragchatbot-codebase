# Testing Framework Changes

## Summary

Enhanced the existing testing framework for the RAG chatbot backend with API endpoint tests, shared fixtures, and cleaner pytest configuration.

## Files Added

### `backend/tests/helpers.py`
Test app factory (`build_test_app`) that creates a minimal FastAPI app mirroring the production endpoints in `app.py` but without the static file mount. This allows endpoint tests to run in CI/test environments where the `frontend/` directory doesn't exist.

### `backend/tests/conftest.py`
Shared pytest fixtures available to all test modules:
- `mock_rag` — `MagicMock` of `RAGSystem` with sensible defaults (session creation, query response, course analytics).
- `client` — `TestClient` wired to the test app using the `mock_rag` fixture.
- `sample_query_payload` — A basic `/api/query` request body.
- `sample_query_payload_with_session` — A `/api/query` request body that includes an existing session ID.

### `backend/tests/test_api_endpoints.py`
16 tests across three endpoint classes:

**`TestQueryEndpoint` (POST /api/query)**
- Returns 200 with `answer`, `sources`, and `session_id` fields.
- Answer text and source data match mock return values.
- Auto-creates a session when none is supplied.
- Uses the provided `session_id` without calling `create_session`.
- Calls `rag.query` with the correct arguments.
- Returns 422 when the required `query` field is missing.
- Returns 500 with the exception message when the RAG system raises.
- Handles backward-compatible plain-string sources (sets `link` to `null`).
- Handles an empty sources list.

**`TestCoursesEndpoint` (GET /api/courses)**
- Returns 200 with `total_courses` and `course_titles`.
- Calls `get_course_analytics` exactly once.
- Returns 500 with the exception message on error.
- Returns an empty catalog correctly.

**`TestDeleteSessionEndpoint` (DELETE /api/session/{session_id})**
- Returns `{"status": "ok"}` with a 200 status.
- Calls `session_manager.delete_session` with the correct session ID.

## Files Modified

### `pyproject.toml`
- Added `httpx>=0.28.0` to `[dependency-groups] dev` (required by FastAPI's `TestClient`).
- Added `[tool.pytest.ini_options]` section:
  - `testpaths = ["backend/tests"]` — pytest discovers tests without specifying the path manually.
  - `pythonpath = ["backend", "backend/tests"]` — makes backend modules and test helpers importable without manual `sys.path` manipulation.
  - `addopts = "-v"` — verbose output by default.
