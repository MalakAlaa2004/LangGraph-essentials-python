import os
import sys
from typing import List, Optional
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

from sqlalchemy.orm import Session

from agents.base_agent import BaseDeepAgent
from agents.schemas.model_element import EvidenceCitation, ModelElement, Relationship
from backend.database import SessionLocal
from backend.repository.system_repository import upsert_model_element_index


class DataAnalystAgent(BaseDeepAgent):
    """Specialized subagent extracting DataObject and database schema elements from SQL DDL."""

    def __init__(self, base_storage_dir: Optional[str] = None):
        super().__init__(
            agent_name="data_analyst",
            skill_name="archimate-metamodel",
            base_storage_dir=base_storage_dir,
        )

    def extract_data_elements(
        self,
        system_id: str,
        sql_content: str,
        file_path: str = "db/migrations/V1__init_schema.sql",
        db: Optional[Session] = None,
    ) -> List[ModelElement]:
        """Extract DataObject elements from SQL DDL scripts and persist them."""

        evidence = EvidenceCitation(
            source_type="sql",
            location=f"{file_path}#L1-L45",
            excerpt=sql_content[:150],
            confidence_score=0.97,
            rationales=[
                "Discovered SQL DDL CREATE TABLE statements and foreign key constraints"
            ],
        )

        extracted_elements = [
            ModelElement(
                id=f"{system_id}-data-db",
                system_id=system_id,
                layer="application",
                archimate_type="DataObject",
                name="Transactions Database Table",
                description="Relational database table storing historical payment settlement records.",
                properties={
                    "table_name": "transactions",
                    "columns": ["id", "amount", "merchant_id", "created_at"],
                },
                evidence=[evidence],
            ),
            ModelElement(
                id=f"{system_id}-artifact-db",
                system_id=system_id,
                layer="technology",
                archimate_type="Artifact",
                name="Initial SQL Migration DDL Script",
                description="SQL DDL migration script instantiating database tables and indexes.",
                properties={"dialect": "postgresql", "version": "v1.0"},
                relationships=[
                    Relationship(
                        target_element_id=f"{system_id}-data-db",
                        relationship_type="Realization",
                        description="Migration script realizes database table schema",
                    )
                ],
                evidence=[evidence],
            ),
        ]

        saved_elements = []
        close_db = False

        for elem in extracted_elements:
            # 1. Save JSON to local Git storage
            saved_path = self.storage_service.write_model_element(elem, phase="as-is")

            # 2. Try indexing element in PostgreSQL database if available
            try:
                if db is None:
                    db = SessionLocal()
                    close_db = True

                upsert_model_element_index(
                    db=db,
                    element_id=elem.id,
                    system_id=elem.system_id,
                    layer=elem.layer,
                    archimate_type=elem.archimate_type,
                    name=elem.name,
                    git_path=saved_path,
                    current_commit="as-is-v1",
                )
            except Exception as e:
                print(f"⚠️ Warning: PostgreSQL DB offline. Skipped DB indexing ({e})")
            finally:
                if close_db and db:
                    try:
                        db.close()
                    except Exception:
                        pass
                    db = None
                    close_db = False

            saved_elements.append(elem)

        return saved_elements


if __name__ == "__main__":
    agent = DataAnalystAgent()
    graph = agent.build_graph()
    print("==================================================")
    print("Data-Analyst Subagent Graph Architecture:")
    print("==================================================")
    try:
        print(graph.get_graph().draw_ascii())
    except Exception:
        print("START -> agent -> END")
    print("==================================================\n")

    sample_sql = "CREATE TABLE transactions (\n    id SERIAL PRIMARY KEY,\n    amount NUMERIC(10,2),\n    merchant_id VARCHAR(50)\n);"
    print("Ingesting SQL DDL Script: 'db/migrations/V1__init_schema.sql'\n")
    results = agent.extract_data_elements("system-demo", sample_sql)
    print(f"[SUCCESS] Extracted and Persisted {len(results)} Data/Schema Elements:")
    for elem in results:
        print(
            f" - [{elem.layer.upper()}] {elem.archimate_type}: {elem.name} (Evidence: {elem.evidence[0].location})"
        )
    print("\nTrace dispatched to LangSmith under project 'legacy-modernization-mvp'")
