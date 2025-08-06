# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
- **Start server**: `./run.sh` or `cd backend && uv run uvicorn app:app --reload --port 8000`
- **Install dependencies**: `uv sync`
- **Access**: Web interface at http://localhost:8000, API docs at http://localhost:8000/docs
- Always use uv to run the server do not use pip directly
- Use uv to run Python files

### Environment Setup
- Requires Python 3.13+ and uv package manager
- Create `.env` file in root with: `ANTHROPIC_API_KEY=your_api_key_here`
- No test suite or linting commands are currently configured
- Make sure to use uv to manage all dependencies

## Architecture Overview

### Core Components
This is a RAG (Retrieval-Augmented Generation) system for querying course materials with the following architecture:

**FastAPI Backend** (`backend/app.py`):
- Main API server with CORS middleware
- Two primary endpoints: `/api/query` for Q&A, `/api/courses` for analytics
- Serves static frontend files from `/frontend/`
- Initializes RAG system on startup and loads documents from `docs/` folder

**RAG System Orchestrator** (`backend/rag_system.py`):
- Central coordinator that manages all RAG components
- Handles document processing, vector storage, AI generation, and session management
- Implements tool-based search approach using `ToolManager` and `CourseSearchTool`
- Processes queries through AI with access to search tools

**Vector Storage** (`backend/vector_store.py`):
- Uses ChromaDB for persistent vector storage with sentence-transformers embeddings
- Manages separate collections for course metadata and content chunks
- Handles deduplication based on course titles
- Model: `all-MiniLM-L6-v2`

**AI Generation** (`backend/ai_generator.py`):
- Interfaces with Anthropic's Claude API (model: `claude-sonnet-4-20250514`)
- Uses tool-calling approach for dynamic course content search
- Includes detailed system prompts for educational responses

**Document Processing** (`backend/document_processor.py`):
- Processes course documents (PDF, DOCX, TXT) into structured data
- Creates `Course` objects with metadata and `CourseChunk` objects for content
- Chunking: 800 chars with 100 char overlap

### Key Configuration
- Document chunks: 800 characters with 100 character overlap
- Vector search: Returns top 5 results
- Session history: Maintains last 2 conversation exchanges
- ChromaDB storage: `./chroma_db` directory

### Data Flow
1. Documents in `docs/` folder are processed into Course and CourseChunk objects
2. Content is embedded and stored in ChromaDB collections
3. User queries trigger AI generation with tool access
4. AI can search vector store via CourseSearchTool during response generation
5. Session manager maintains conversation context

### Frontend
Simple HTML/CSS/JS interface (`frontend/`) for web-based interaction with the RAG system.