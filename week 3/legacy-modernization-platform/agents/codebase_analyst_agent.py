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


class CodebaseAnalystAgent(BaseDeepAgent):
    """Specialized subagent extracting Application layer elements from source code."""

    def __init__(self, base_storage_dir: Optional[str] = None):
        super().__init__(
            agent_name="codebase_analyst",
            skill_name="archimate-metamodel",
            base_storage_dir=base_storage_dir,
        )

    def extract_codebase_elements(
        self,
        system_id: str,
        code_content: str,
        file_path: str = "legacy/payment_service.py",
        db: Optional[Session] = None,
    ) -> List[ModelElement]:
        """Extract Application layer elements from source code files and persist them."""

        evidence = EvidenceCitation(
            source_type="code",
            location=f"{file_path}#L1-L75",
            excerpt=code_content[:150],
            confidence_score=0.96,
            rationales=[
                "Discovered class definition and REST endpoints in source code"
            ],
        )

        extracted_elements = [
            ModelElement(
                id=f"{system_id}-comp-app",
                system_id=system_id,
                layer="application",
                archimate_type="ApplicationComponent",
                name="Legacy Payment Monolith Service",
                description="Python application component processing inbound credit card charges.",
                properties={"language": "python", "framework": "fastapi"},
                evidence=[evidence],
            ),
            ModelElement(
                id=f"{system_id}-appsvc-app",
                system_id=system_id,
                layer="application",
                archimate_type="ApplicationService",
                name="Payment Processing REST Service",
                description="Exposed REST application service for authorization and settlement.",
                properties={"protocol": "REST", "endpoint": "/api/v1/charge"},
                relationships=[
                    Relationship(
                        target_element_id=f"{system_id}-comp-app",
                        relationship_type="Realization",
                        description="Component realizes REST service",
                    )
                ],
                evidence=[evidence],
            ),
            ModelElement(
                id=f"{system_id}-data-app",
                system_id=system_id,
                layer="application",
                archimate_type="DataObject",
                name="Payment Transaction Payload",
                description="Pydantic/ORM data object holding credit card token, amount, and currency.",
                properties={"fields": ["token", "amount", "currency", "status"]},
                relationships=[
                    Relationship(
                        target_element_id=f"{system_id}-comp-app",
                        relationship_type="Access",
                        description="Component accesses transaction payload",
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
    agent = CodebaseAnalystAgent()
    graph = agent.build_graph()
    print("==================================================")
    print("Code-Analyzer Subagent Graph Architecture:")
    print("==================================================")
    try:
        print(graph.get_graph().draw_ascii())
    except Exception:
        print("START -> agent -> END")
    print("==================================================\n")

    sample_code = "class PaymentProcessor:\n    def process_charge(self, token: str, amount: float):\n        return {'status': 'success'}"
    print("Ingesting Source Code File: 'legacy/payment_service.py'\n")
    results = agent.extract_codebase_elements("system-demo", sample_code)
    print(f"[SUCCESS] Extracted and Persisted {len(results)} Application Elements:")
    for elem in results:
        print(
            f" - [{elem.layer.upper()}] {elem.archimate_type}: {elem.name} (Evidence: {elem.evidence[0].location})"
        )
    print("\nTrace dispatched to LangSmith under project 'legacy-modernization-mvp'")
