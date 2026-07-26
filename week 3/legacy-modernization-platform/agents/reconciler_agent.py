import os
import sys
from typing import Dict, List, Optional
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

from sqlalchemy.orm import Session

from agents.base_agent import BaseDeepAgent
from agents.schemas.model_element import ModelElement
from backend.database import SessionLocal
from backend.repository.system_repository import upsert_model_element_index


class ReconcilerAgent(BaseDeepAgent):
    """Specialized subagent reconciling and deduplicating extracted ArchiMate elements."""

    def __init__(self, base_storage_dir: Optional[str] = None):
        super().__init__(
            agent_name="reconciler",
            skill_name="archimate-metamodel",
            base_storage_dir=base_storage_dir,
        )

    def reconcile_elements(
        self,
        elements: List[ModelElement],
        db: Optional[Session] = None,
    ) -> List[ModelElement]:
        """Merge duplicate elements with identical names and layers into canonical elements."""

        reconciled_map: Dict[str, ModelElement] = {}

        for elem in elements:
            key = f"{elem.layer.lower()}:{elem.name.lower().strip()}"
            if key not in reconciled_map:
                reconciled_map[key] = elem
            else:
                existing = reconciled_map[key]
                # Merge evidence citations
                existing_locs = {ev.location for ev in existing.evidence}
                for ev in elem.evidence:
                    if ev.location not in existing_locs:
                        existing.evidence.append(ev)

                # Merge relationships
                existing_rel_ids = {r.target_element_id for r in existing.relationships}
                for rel in elem.relationships:
                    if rel.target_element_id not in existing_rel_ids:
                        existing.relationships.append(rel)

                # Merge properties
                existing.properties.update(elem.properties)

        reconciled_list = list(reconciled_map.values())

        # Persist reconciled canonical elements
        close_db = False
        for elem in reconciled_list:
            saved_path = self.storage_service.write_model_element(elem, phase="as-is")
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
                    current_commit="reconciled-v1",
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

        return reconciled_list


if __name__ == "__main__":
    agent = ReconcilerAgent()
    graph = agent.build_graph()
    print("==================================================")
    print("Reconciler Subagent Graph Architecture:")
    print("==================================================")
    try:
        print(graph.get_graph().draw_ascii())
    except Exception:
        print("START -> agent -> END")
    print("==================================================\n")

    elem1 = ModelElement(
        id="comp-001",
        system_id="system-demo",
        layer="application",
        archimate_type="ApplicationComponent",
        name="Legacy Payment Monolith",
        description="Payment processing monolith component.",
    )
    elem2 = ModelElement(
        id="comp-dup",
        system_id="system-demo",
        layer="application",
        archimate_type="ApplicationComponent",
        name="Legacy Payment Monolith",
        description="Duplicate payment processing monolith component.",
    )

    print("Reconciling Duplicate Elements for 'Legacy Payment Monolith'...\n")
    results = agent.reconcile_elements([elem1, elem2])
    print(f"[SUCCESS] Reconciled {len(results)} Canonical Element(s):")
    for r in results:
        print(f" - [{r.layer.upper()}] {r.archimate_type}: {r.name} (ID: {r.id})")
    print("\nTrace dispatched to LangSmith under project 'legacy-modernization-mvp'")
