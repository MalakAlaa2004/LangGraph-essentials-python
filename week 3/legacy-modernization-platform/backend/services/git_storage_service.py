import os
from typing import List, Optional
from agents.schemas.model_element import ModelElement


class GitStorageService:
    """Service handling reading, writing, and listing ModelElement JSON files in model repository."""

    def __init__(self, base_dir: str):
        self.base_dir = os.path.abspath(base_dir)

    def get_system_phase_dir(self, system_id: str, phase: str = "as-is") -> str:
        return os.path.join(self.base_dir, "systems", system_id, phase)

    def read_model_element(
        self, system_id: str, layer: str, element_id: str, phase: str = "as-is"
    ) -> Optional[ModelElement]:
        """Read and validate a ModelElement JSON file from storage."""
        file_path = os.path.join(
            self.get_system_phase_dir(system_id, phase), layer, f"{element_id}.json"
        )
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return ModelElement.model_validate_json(content)

    def write_model_element(self, element: ModelElement, phase: str = "as-is") -> str:
        """Write and validate a ModelElement JSON file to storage."""
        layer_dir = os.path.join(
            self.get_system_phase_dir(element.system_id, phase), element.layer
        )
        os.makedirs(layer_dir, exist_ok=True)
        file_path = os.path.join(layer_dir, f"{element.id}.json")

        json_data = element.model_dump_json(indent=2)
        ModelElement.model_validate_json(json_data)  # Re-validate before saving

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_data)
        return file_path

    def list_model_elements(
        self, system_id: str, phase: str = "as-is", layer: Optional[str] = None
    ) -> List[ModelElement]:
        """List all ModelElement objects for a system and phase."""
        elements = []
        phase_dir = self.get_system_phase_dir(system_id, phase)
        if not os.path.exists(phase_dir):
            return elements

        layers_to_scan = [layer] if layer else os.listdir(phase_dir)
        for l in layers_to_scan:
            layer_dir = os.path.join(phase_dir, l)
            if os.path.isdir(layer_dir):
                for filename in os.listdir(layer_dir):
                    if filename.endswith(".json"):
                        file_path = os.path.join(layer_dir, filename)
                        with open(file_path, "r", encoding="utf-8") as f:
                            elements.append(ModelElement.model_validate_json(f.read()))
        return elements
