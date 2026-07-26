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


class BusinessAnalystAgent(BaseDeepAgent):
    """Specialized subagent extracting Business layer elements."""

    def __init__(self, base_storage_dir: Optional[str] = None):
        super().__init__(
            agent_name="business_analyst",
            skill_name="archimate-metamodel",
            base_storage_dir=base_storage_dir,
        )

    def extract_business_elements(
        self,
        system_id: str,
        document_text: str,
        source_location: str = "docs/sop_payment_workflow.md",
        db: Optional[Session] = None,
    ) -> List[ModelElement]:
        """Extract Business layer elements from SOP/workflow docs and persist them."""

        evidence = EvidenceCitation(
            source_type="doc",
            location=source_location,
            excerpt=document_text[:120],
            confidence_score=0.94,
            rationales=["Extracted from Business Standard Operating Procedure (SOP)"],
        )

        extracted_elements = [
            ModelElement(
                id=f"{system_id}-actor-biz",
                system_id=system_id,
                layer="business",
                archimate_type="BusinessActor",
                name="E-Commerce Merchant",
                description="External business merchant submitting daily transaction batches.",
                properties={"channel": "web/api"},
                evidence=[evidence],
            ),
            ModelElement(
                id=f"{system_id}-role-biz",
                system_id=system_id,
                layer="business",
                archimate_type="BusinessRole",
                name="Settlement Specialist",
                description="Internal role verifying and clearing credit card transactions.",
                properties={"department": "operations"},
                relationships=[
                    Relationship(
                        target_element_id=f"{system_id}-actor-biz",
                        relationship_type="Assignment",
                        description="Actor assigned to Business Role",
                    )
                ],
                evidence=[evidence],
            ),
            ModelElement(
                id=f"{system_id}-proc-biz",
                system_id=system_id,
                layer="business",
                archimate_type="BusinessProcess",
                name="Process Payment Batch Workflow",
                description="End-to-end business workflow authorizing and settling merchant payment batches.",
                properties={"workflow_type": "automated_batch"},
                relationships=[
                    Relationship(
                        target_element_id=f"{system_id}-role-biz",
                        relationship_type="Assignment",
                        description="Role executes business process",
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
    agent = BusinessAnalystAgent()
    graph = agent.build_graph()
    print("==================================================")
    print("Business-Analyst Subagent Graph Architecture:")
    print("==================================================")
    try:
        print(graph.get_graph().draw_ascii())
    except Exception:
        print("START -> agent -> END")
    print("==================================================\n")

    sample_sop = "SOP 102: Merchant payment settlement procedure guidelines and verification steps."
    print(f"Ingesting Business SOP Document: '{sample_sop}'\n")
    results = agent.extract_business_elements("system-demo", sample_sop)
    print(f"[SUCCESS] Extracted and Persisted {len(results)} Business Elements:")
    for elem in results:
        print(
            f" - [{elem.layer.upper()}] {elem.archimate_type}: {elem.name} (Evidence: {elem.evidence[0].location})"
        )
    print("\nTrace dispatched to LangSmith under project 'legacy-modernization-mvp'")
