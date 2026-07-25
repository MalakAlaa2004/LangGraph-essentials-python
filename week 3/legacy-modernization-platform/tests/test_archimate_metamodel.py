import os
from agents.skills import archimate_metamodel_parser as parser


def test_archimate_layers():
    assert "motivation" in parser.VALID_LAYERS
    assert "strategy" in parser.VALID_LAYERS
    assert "business" in parser.VALID_LAYERS
    assert "application" in parser.VALID_LAYERS
    assert "technology" in parser.VALID_LAYERS


def test_valid_element_types():
    assert parser.is_valid_element_type("ApplicationComponent")
    assert parser.get_element_layer("ApplicationComponent") == "application"

    assert parser.is_valid_element_type("BusinessProcess")
    assert parser.get_element_layer("BusinessProcess") == "business"

    assert parser.is_valid_element_type("Node")
    assert parser.get_element_layer("Node") == "technology"

    assert not parser.is_valid_element_type("FakeInvalidElement")


def test_valid_relationship_types():
    assert parser.is_valid_relationship_type("Realization")
    assert parser.is_valid_relationship_type("Serving")
    assert parser.is_valid_relationship_type("Triggering")
    assert not parser.is_valid_relationship_type("FakeRelationship")


def test_skill_file_exists():
    skill_path = os.path.join("agents", "skills", "archimate-metamodel", "SKILL.md")
    assert os.path.exists(skill_path)
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "name: archimate-metamodel" in content
    assert "ArchiMate 3.2 Metamodel Specification" in content
