import os
from agents.schemas.model_element import ModelElement
from backend.fixtures_generator import generate_fixtures


def test_generate_fixtures(tmp_path):
    output_dir = str(tmp_path)
    created_files = generate_fixtures(output_dir, system_id="test-sys", phase="as-is")

    assert len(created_files) == 12

    # Verify all 5 layers created
    layers_found = set()
    for file_path in created_files:
        assert os.path.exists(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify 100% schema validation
        element = ModelElement.model_validate_json(content)
        assert element.system_id == "test-sys"
        layers_found.add(element.layer)

    assert layers_found == {
        "motivation",
        "strategy",
        "business",
        "application",
        "technology",
    }
