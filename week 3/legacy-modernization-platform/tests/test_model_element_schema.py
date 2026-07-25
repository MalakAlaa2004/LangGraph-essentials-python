import pytest
from pydantic import ValidationError
from agents.schemas.model_element import EvidenceCitation, Relationship, ModelElement


def test_valid_model_element_serialization():
    evidence = EvidenceCitation(
        source_type="code",
        location="backend/app.py#L12-L30",
        excerpt="class OrderProcessor:",
        confidence_score=0.95,
        rationales=["Direct class declaration found in codebase"],
    )

    relationship = Relationship(
        target_element_id="elem-db-001",
        relationship_type="Access",
        description="Reads order payload",
        evidence=[evidence],
    )

    element = ModelElement(
        id="elem-app-001",
        system_id="sys-demo",
        layer="application",
        archimate_type="ApplicationComponent",
        name="OrderProcessor",
        description="Processes inbound orders",
        properties={"language": "python", "framework": "fastapi"},
        relationships=[relationship],
        evidence=[evidence],
    )

    # Test serialization to dict and JSON
    data_dict = element.model_dump()
    assert data_dict["archimate_type"] == "ApplicationComponent"
    assert data_dict["evidence"][0]["confidence_score"] == 0.95

    json_str = element.model_dump_json()
    assert "OrderProcessor" in json_str


def test_invalid_confidence_score_raises_error():
    with pytest.raises(ValidationError) as exc_info:
        EvidenceCitation(
            source_type="code",
            location="file.py",
            excerpt="code",
            confidence_score=1.5,  # Invalid: > 1.0
        )
    assert "confidence_score must be between 0.0 and 1.0" in str(exc_info.value)


def test_invalid_archimate_type_raises_error():
    with pytest.raises(ValidationError) as exc_info:
        ModelElement(
            id="elem-1",
            system_id="sys-1",
            layer="application",
            archimate_type="FakeComponent",  # Invalid type
            name="Fake",
            description="Fake",
        )
    assert "is not a valid ArchiMate 3.2 element type" in str(exc_info.value)


def test_invalid_relationship_type_raises_error():
    with pytest.raises(ValidationError) as exc_info:
        Relationship(
            target_element_id="elem-2",
            relationship_type="InvalidRelType",  # Invalid relationship
        )
    assert "is not a valid ArchiMate 3.2 relationship type" in str(exc_info.value)
