# Database Schema Documentation — MVP (Task B1)

The Phase 1 MVP uses PostgreSQL with 5 core relational tables managed by Alembic migrations.

## Entity Relationship Diagram

```mermaid
erDiagram
    legacy_systems ||--o{ model_element_index : "indexes"
    legacy_systems ||--o{ artifact_versions : "versions"
    legacy_systems ||--o{ jobs : "executes"
    legacy_systems ||--o{ evidence_sources : "ingests"

    legacy_systems {
        string id PK
        string name
        string description
        datetime created_at
    }

    model_element_index {
        string id PK
        string system_id FK
        string layer
        string archimate_type
        string name
        string git_path
        string current_commit
        datetime updated_at
    }

    artifact_versions {
        string id PK
        string system_id FK
        string commit_sha
        string phase
        string tag
        string author_type
        string run_id
        string approval_status
        string approved_by
        datetime approved_at
        datetime created_at
    }

    jobs {
        string id PK
        string system_id FK
        string phase
        string status
        string run_id
        text error_message
        datetime started_at
        datetime finished_at
    }

    evidence_sources {
        string id PK
        string system_id FK
        string source_type
        string location
        text description
        datetime added_at
    }
```

## Table Descriptions

1. **`legacy_systems`**: Master registry of legacy software applications.
2. **`model_element_index`**: Lightweight queryable relational index of ArchiMate 3.2 elements stored as JSON in Git.
3. **`artifact_versions`**: Audit trail joining LangSmith trace `run_id` to Git `commit_sha` and human PR `approval_status`.
4. **`jobs`**: Tracks asynchronous background agent runs (`queued`, `running`, `succeeded`, `failed`).
5. **`evidence_sources`**: Ingestion locations for source code, IaC, docs, and interview transcripts.
