from agents.schemas.model_element import ModelElement, Relationship
from agents.validator_agent import ValidatorAgent


def test_validator_graph_audit():
    agent = ValidatorAgent()

    elem1 = ModelElement(
        id="comp-1",
        system_id="system-demo",
        layer="application",
        archimate_type="ApplicationComponent",
        name="Monolith Component",
        description="Valid component",
        relationships=[
            Relationship(
                target_element_id="comp-2",
                relationship_type="Serving",
                description="Serving component",
            )
        ],
    )
    elem2 = ModelElement(
        id="comp-2",
        system_id="system-demo",
        layer="application",
        archimate_type="ApplicationService",
        name="REST Service",
        description="Valid service",
    )

    report = agent.validate_graph([elem1, elem2])
    assert report["total_elements"] == 2
    assert report["error_count"] == 0
    assert report["completeness_score"] == 100.0
