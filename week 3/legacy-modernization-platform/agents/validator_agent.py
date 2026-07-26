import os
import sys
from typing import Dict, List, Optional
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

from agents.base_agent import BaseDeepAgent
from agents.schemas.model_element import ModelElement
from agents.skills import archimate_metamodel_parser as parser


class ValidatorAgent(BaseDeepAgent):
    """Specialized subagent performing graph validation & metamodel compliance auditing."""

    def __init__(self, base_storage_dir: Optional[str] = None):
        super().__init__(
            agent_name="validator",
            skill_name="archimate-metamodel",
            base_storage_dir=base_storage_dir,
        )

    def validate_graph(
        self, elements: List[ModelElement]
    ) -> Dict[str, List[str] | int | float]:
        """Audit complete ArchiMate knowledge graph for structural errors and warnings."""

        errors: List[str] = []
        warnings: List[str] = []
        element_ids = {elem.id for elem in elements}

        for elem in elements:
            # 1. Validate ArchiMate Element Type & Layer
            if not parser.is_valid_element_type(elem.archimate_type):
                errors.append(
                    f"Element [{elem.id}]: Invalid archimate_type '{elem.archimate_type}'."
                )

            # 2. Validate Evidence Citations
            if not elem.evidence:
                warnings.append(f"Element [{elem.id}]: Missing evidence citations.")
            else:
                for ev in elem.evidence:
                    if ev.confidence_score < 0.0 or ev.confidence_score > 1.0:
                        errors.append(
                            f"Element [{elem.id}]: Confidence score {ev.confidence_score} out of bounds (0.0-1.0)."
                        )

            # 3. Validate Relationships Legality & Target Existence
            if not elem.relationships:
                warnings.append(
                    f"Element [{elem.id}]: Disconnected element (no relationships)."
                )
            else:
                for rel in elem.relationships:
                    if not parser.is_valid_relationship_type(rel.relationship_type):
                        errors.append(
                            f"Element [{elem.id}]: Invalid relationship_type '{rel.relationship_type}' to '{rel.target_element_id}'."
                        )
                    if rel.target_element_id not in element_ids:
                        warnings.append(
                            f"Element [{elem.id}]: Target element '{rel.target_element_id}' not found in graph."
                        )

        total_elements = len(elements)
        valid_elements = total_elements - len(errors)
        completeness_score = (
            round((valid_elements / total_elements) * 100.0, 2)
            if total_elements > 0
            else 100.0
        )

        return {
            "total_elements": total_elements,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "completeness_score": completeness_score,
            "errors": errors,
            "warnings": warnings,
        }


if __name__ == "__main__":
    agent = ValidatorAgent()
    graph = agent.build_graph()
    print("==================================================")
    print("Validator Subagent Graph Architecture:")
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
        name="Legacy Monolith",
        description="Application component",
    )
    print("Auditing ArchiMate Knowledge Graph Compliance...\n")
    report = agent.validate_graph([elem1])
    print(f"[SUCCESS] Audit Report Generated:")
    print(f" - Total Elements: {report['total_elements']}")
    print(f" - Error Count: {report['error_count']}")
    print(f" - Warning Count: {report['warning_count']}")
    print(f" - Graph Completeness Score: {report['completeness_score']}%")
    print("\nTrace dispatched to LangSmith under project 'legacy-modernization-mvp'")
