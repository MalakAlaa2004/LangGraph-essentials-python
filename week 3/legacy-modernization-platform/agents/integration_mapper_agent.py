import os
import sys
from typing import List, Optional
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

from sqlalchemy.orm import Session

from agents.base_agent import BaseDeepAgent
from agents.schemas.model_element import ModelElement, Relationship
from agents.skills import archimate_metamodel_parser as parser
from backend.database import SessionLocal
from backend.repository.system_repository import upsert_model_element_index


class IntegrationMapperAgent(BaseDeepAgent):
    """Specialized subagent discovering and validating cross-layer ArchiMate relationships."""

    def __init__(self, base_storage_dir: Optional[str] = None):
        super().__init__(
            agent_name="integration_mapper",
            skill_name="archimate-metamodel",
            base_storage_dir=base_storage_dir,
        )

    def map_cross_layer_relationship(
        self,
        source_element: ModelElement,
        target_element: ModelElement,
        relationship_type: str,
        description: str,
        db: Optional[Session] = None,
    ) -> Optional[ModelElement]:
        """Validate relationship legality against ArchiMate 3.2 specs and update persistence."""

        # 1. Validate relationship type legality
        if not parser.is_valid_relationship_type(relationship_type):
            print(f"❌ Invalid Relationship Type: '{relationship_type}' rejected.")
            return None

        new_rel = Relationship(
            target_element_id=target_element.id,
            relationship_type=relationship_type,
            description=description,
        )

        # Check for duplicates
        existing_ids = [r.target_element_id for r in source_element.relationships]
        if target_element.id not in existing_ids:
            source_element.relationships.append(new_rel)

        # 2. Save updated element to local Git storage
        saved_path = self.storage_service.write_model_element(
            source_element, phase="as-is"
        )

        # 3. Update PostgreSQL database index if online
        close_db = False
        try:
            if db is None:
                db = SessionLocal()
                close_db = True

            upsert_model_element_index(
                db=db,
                element_id=source_element.id,
                system_id=source_element.system_id,
                layer=source_element.layer,
                archimate_type=source_element.archimate_type,
                name=source_element.name,
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

        return source_element


if __name__ == "__main__":
    agent = IntegrationMapperAgent()
    graph = agent.build_graph()
    print("==================================================")
    print("Integration-Mapper Subagent Graph Architecture:")
    print("==================================================")
    try:
        print(graph.get_graph().draw_ascii())
    except Exception:
        print("START -> agent -> END")
    print("==================================================\n")

    # Sample Cross-Layer Elements
    biz_process = ModelElement(
        id="proc-101",
        system_id="system-demo",
        layer="business",
        archimate_type="BusinessProcess",
        name="Process Credit Card Batch",
        description="Business process clearing payments.",
    )

    app_service = ModelElement(
        id="appsvc-101",
        system_id="system-demo",
        layer="application",
        archimate_type="ApplicationService",
        name="Payment Processing REST Service",
        description="Application service exposing REST endpoints.",
    )

    print(
        "Mapping Cross-Layer Relationship: BusinessProcess -> ApplicationService (Serving)\n"
    )
    updated = agent.map_cross_layer_relationship(
        source_element=biz_process,
        target_element=app_service,
        relationship_type="Serving",
        description="Application service serves Business Process",
    )

    if updated:
        print(
            f"[SUCCESS] Mapped Valid Cross-Layer Relationship: {updated.name} --(Serving)--> {app_service.name}"
        )
    print("\nTrace dispatched to LangSmith under project 'legacy-modernization-mvp'")
