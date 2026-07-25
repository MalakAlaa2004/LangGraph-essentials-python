from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from agents.skills.archimate_metamodel_parser import (
    VALID_LAYERS,
    is_valid_element_type,
    is_valid_relationship_type,
)


class EvidenceCitation(BaseModel):
    """Schema representing evidence supporting an architectural claim."""

    source_type: str = Field(
        ..., description="Source category: code, iac, doc, transcript"
    )
    location: str = Field(
        ..., description="File path, line range, or URI location of evidence"
    )
    excerpt: str = Field(..., description="Raw text snippet or code excerpt")
    confidence_score: float = Field(..., description="Confidence score from 0.0 to 1.0")
    rationales: List[str] = Field(
        default_factory=list, description="Reasoning for this citation"
    )

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence_score(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0 inclusive")
        return v


class Relationship(BaseModel):
    """Schema representing an ArchiMate 3.2 relationship between elements."""

    target_element_id: str = Field(..., description="Target ArchiMate element ID")
    relationship_type: str = Field(..., description="ArchiMate 3.2 relationship type")
    description: Optional[str] = Field(
        None, description="Description of the relationship"
    )
    evidence: List[EvidenceCitation] = Field(
        default_factory=list, description="Citations supporting relationship"
    )

    @field_validator("relationship_type")
    @classmethod
    def validate_relationship_type(cls, v: str) -> str:
        if not is_valid_relationship_type(v):
            raise ValueError(f"'{v}' is not a valid ArchiMate 3.2 relationship type")
        return v


class ModelElement(BaseModel):
    """Canonical schema for an ArchiMate 3.2 model element."""

    id: str = Field(..., description="Unique element identifier")
    system_id: str = Field(..., description="System identifier")
    layer: str = Field(
        ...,
        description="ArchiMate layer: motivation, strategy, business, application, technology",
    )
    archimate_type: str = Field(..., description="ArchiMate 3.2 element type")
    name: str = Field(..., description="Title/name of the element")
    description: str = Field(..., description="Detailed description of the element")
    properties: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary metadata properties"
    )
    relationships: List[Relationship] = Field(
        default_factory=list, description="Connected relationships"
    )
    evidence: List[EvidenceCitation] = Field(
        default_factory=list, description="Citations supporting element"
    )
    created_by_run_id: Optional[str] = Field(None, description="LangSmith trace run_id")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of creation"
    )

    @field_validator("layer")
    @classmethod
    def validate_layer(cls, v: str) -> str:
        v_lower = v.lower()
        if v_lower not in VALID_LAYERS:
            raise ValueError(
                f"'{v}' is not a valid ArchiMate layer. Must be one of: {VALID_LAYERS}"
            )
        return v_lower

    @field_validator("archimate_type")
    @classmethod
    def validate_archimate_type(cls, v: str) -> str:
        if not is_valid_element_type(v):
            raise ValueError(f"'{v}' is not a valid ArchiMate 3.2 element type")
        return v
