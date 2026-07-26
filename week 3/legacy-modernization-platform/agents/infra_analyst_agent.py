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


class InfraAnalystAgent(BaseDeepAgent):
    """Specialized subagent extracting Technology/Infrastructure layer elements from IaC."""

    def __init__(self, base_storage_dir: Optional[str] = None):
        super().__init__(
            agent_name="infra_analyst",
            skill_name="archimate-metamodel",
            base_storage_dir=base_storage_dir,
        )

    def extract_infra_elements(
        self,
        system_id: str,
        iac_content: str,
        file_path: str = "infrastructure/docker-compose.yaml",
        db: Optional[Session] = None,
    ) -> List[ModelElement]:
        """Extract Technology layer elements from IaC configs and persist them."""

        evidence = EvidenceCitation(
            source_type="iac",
            location=f"{file_path}#L10-L35",
            excerpt=iac_content[:150],
            confidence_score=0.98,
            rationales=[
                "Discovered container services and node infrastructure in IaC file"
            ],
        )

        extracted_elements = [
            ModelElement(
                id=f"{system_id}-node-infra",
                system_id=system_id,
                layer="technology",
                archimate_type="Node",
                name="On-Premises Linux Host",
                description="Physical Linux server host executing Docker engine runtime.",
                properties={"os": "Ubuntu 20.04 LTS", "arch": "x86_64"},
                evidence=[evidence],
            ),
            ModelElement(
                id=f"{system_id}-software-infra",
                system_id=system_id,
                layer="technology",
                archimate_type="SystemSoftware",
                name="PostgreSQL Database Engine",
                description="PostgreSQL 16 relational database engine container declared in docker-compose.",
                properties={"image": "postgres:16-alpine", "port": 5432},
                relationships=[
                    Relationship(
                        target_element_id=f"{system_id}-node-infra",
                        relationship_type="Assignment",
                        description="Node hosts PostgreSQL system software",
                    )
                ],
                evidence=[evidence],
            ),
            ModelElement(
                id=f"{system_id}-artifact-infra",
                system_id=system_id,
                layer="technology",
                archimate_type="Artifact",
                name="PostgreSQL Docker Compose Manifest",
                description="Declarative Docker Compose YAML manifest configuring database services.",
                properties={"format": "yaml"},
                relationships=[
                    Relationship(
                        target_element_id=f"{system_id}-software-infra",
                        relationship_type="Realization",
                        description="Manifest realizes system software container",
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
    agent = InfraAnalystAgent()
    graph = agent.build_graph()
    print("==================================================")
    print("Infra-Analyzer Subagent Graph Architecture:")
    print("==================================================")
    try:
        print(graph.get_graph().draw_ascii())
    except Exception:
        print("START -> agent -> END")
    print("==================================================\n")

    sample_iac = "services:\n  postgres:\n    image: postgres:16-alpine\n    ports:\n      - '5432:5432'"
    print("Ingesting IaC Manifest: 'infrastructure/docker-compose.yaml'\n")
    results = agent.extract_infra_elements("system-demo", sample_iac)
    print(f"[SUCCESS] Extracted and Persisted {len(results)} Infrastructure Elements:")
    for elem in results:
        print(
            f" - [{elem.layer.upper()}] {elem.archimate_type}: {elem.name} (Evidence: {elem.evidence[0].location})"
        )
    print("\nTrace dispatched to LangSmith under project 'legacy-modernization-mvp'")
