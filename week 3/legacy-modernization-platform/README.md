# ⚡ Legacy System Modernization Platform (MVP Phase 1)

> **Multi-Agent Enterprise Architecture Extraction & Modernization Graph Platform**  
> Built with Python 3.10+, LangChain, LangGraph, Pydantic v2, FastAPI, PostgreSQL, and Open Group ArchiMate 3.2 Metamodel Specification.

---

## 🌟 Overview & System Architecture

The **Legacy System Modernization Platform** automates the reverse-engineering of complex legacy software applications into formal, machine-readable **ArchiMate 3.2 Knowledge Graphs**. Specialized domain subagents analyze strategy documents, business SOPs, application source code, database schemas, and Infrastructure-as-Code (IaC) manifests to construct an end-to-end ArchiMate architecture model with full line-location evidence traceability.

```text
===================================================================================
Top-Level Phase 1 Orchestrator Pipeline Architecture:
===================================================================================
START ➔ [Strategy] ➔ [Business] ➔ [Codebase] ➔ [Infra] ➔ [Data] ➔ [Reconciler] ➔ [Validator] ➔ END
===================================================================================
```

---

## 🏛️ ArchiMate 3.2 Layer Coverage

Our metamodel skill (`agents/skills/archimate-metamodel/SKILL.md`) covers the **5 core software MVP layers**:

1. **Motivation Layer:** `Goal`, `Driver`, `Assessment`, `Requirement`, `Constraint`
2. **Strategy Layer:** `Resource`, `Capability`, `CourseOfAction`, `ValueStream`
3. **Business Layer:** `BusinessActor`, `BusinessRole`, `BusinessProcess`, `BusinessService`
4. **Application Layer:** `ApplicationComponent`, `ApplicationService`, `ApplicationInterface`, `DataObject`
5. **Technology Layer:** `Node`, `Device`, `SystemSoftware`, `TechnologyService`, `Artifact`

---

## 🚀 Quickstart & Setup Guide

### 1. Environment Requirements
* **Python:** `>=3.10`
* **Database:** PostgreSQL 16 (via Docker Compose)
* **LLM Engine:** Ollama / OpenAI API / LangChain integration

### 2. Installation & Virtual Environment Setup
```powershell
# Clone repository
git clone https://github.com/MalakAlaa2004/LangGraph-essentials-python.git
cd "week 3/legacy-modernization-platform"

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. PostgreSQL Database Setup
```powershell
# Start local PostgreSQL container
docker compose up -d

# Apply Alembic schema migrations
.\.venv\Scripts\alembic.exe upgrade head
```

### 4. Running the Backend REST API & Web Dashboard
```powershell
# Start FastAPI backend server (includes embedded Web UI)
.\.venv\Scripts\uvicorn.exe backend.api:app --reload --port 8000
```
Open your browser to:
* **Web UI Dashboard:** `http://localhost:8000/`
* **Swagger REST API Docs:** `http://localhost:8000/docs`

---

## 🧪 Running the Pytest Test Suite

Execute all 41+ unit & integration tests across Epics A through J:

```powershell
.\.venv\Scripts\pytest.exe
```

---

