# Legacy Modernization Platform — Phase 1 MVP

A multi-agent platform for documenting, assessing, and modernizing legacy system architectures using Deep Agents (LangGraph/LangChain).

## Project Structure
- `backend/`: FastAPI application, endpoints, and database models.
- `agents/`: Deep Agents runtime, subagent prompts, and skills.
- `frontend/`: React + Vite model viewer user interface.
- `docs/`: Architecture specifications and diagrams.
- `test-fixtures/`: Sample legacy codebase and evidence files.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd legacy-modernization-platform
## Database Setup (Task A2)

1. **Start PostgreSQL Container:**
   ```bash
   docker compose up -d
