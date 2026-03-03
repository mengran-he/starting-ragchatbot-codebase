"""Shared helpers for building a test FastAPI app without static file mounts."""
from unittest.mock import MagicMock
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional


def build_test_app(mock_rag: MagicMock) -> FastAPI:
    """Return a minimal FastAPI app backed by a mock RAG system.

    Mirrors the endpoints in app.py but omits the static-file mount so the
    app can be used in environments where the frontend directory doesn't exist.
    """
    app = FastAPI(title="Test RAG API")

    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class SourceInfo(BaseModel):
        text: str
        link: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[SourceInfo]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = mock_rag.session_manager.create_session()
            answer, sources = mock_rag.query(request.query, session_id)
            source_infos = []
            for source in sources:
                if isinstance(source, dict):
                    source_infos.append(SourceInfo(
                        text=source.get("text", ""),
                        link=source.get("link"),
                    ))
                else:
                    source_infos.append(SourceInfo(text=str(source)))
            return QueryResponse(answer=answer, sources=source_infos, session_id=session_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = mock_rag.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"],
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/session/{session_id}")
    async def delete_session(session_id: str):
        mock_rag.session_manager.delete_session(session_id)
        return {"status": "ok"}

    return app
