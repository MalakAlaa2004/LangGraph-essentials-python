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

## 📑 Completed Epics Summary

| Epic | Subsystem / Components | Task Range | Status |
| :--- | :--- | :---: | :---: |
| **Epic A** | Scaffolding, PostgreSQL DB, GitHub Repo & LangSmith Tracing | A1 – A4 | ✅ 100% Done |
| **Epic B** | Core Database Schema, Alembic Migrations & Repository CRUD | B1 – B2 | ✅ 100% Done |
| **Epic C** | ArchiMate 3.2 Metamodel Skill & Smoke-Test Agent | C1 – C2 | ✅ 100% Done |
| **Epic D** | Canonical Schemas, Fixtures Generator, Base Deep Agent & Pipeline | D0 – D3 | ✅ 100% Done |
| **Epic E** | Specialized Domain Ingestion Subagents (Strategy, Business, Code, Infra, Data) | E1 – E5 | ✅ 100% Done |
| **Epic F** | Reconciler (Deduplication) & Validator (Compliance Audit) | F1 – F2 | ✅ 100% Done |
| **Epic G** | GitHub PR Tools & Webhook Receiver (`POST /webhooks/github`) | G1 – G3 | ✅ 100% Done |
| **Epic H** | Top-Level Orchestrator, Async Job Runner & REST API | H1 – H3 | ✅ 100% Done |
| **Epic I** | Web Dashboard UI (Glassmorphic Interface & Element Browser) | I1 – I4 | ✅ 100% Done |
| **Epic J** | Demo Evidence Set, E2E Acceptance Test & Developer Runbook | J1 – J3 | ✅ 100% Done |

---

## 👨‍💻 Submission & Video Walkthrough Notes (For Hassan El-Hadidy)

* **GitHub Repository:** [https://github.com/MalakAlaa2004/LangGraph-essentials-python.git](https://github.com/MalakAlaa2004/LangGraph-essentials-python.git)
* **Google Drive Link:** [Shared Public Drive for Video Recordings]
* **Observability:** All LLM calls and graph execution traces are logged in **LangSmith** under project `legacy-modernization-mvp`.
