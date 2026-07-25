"""Python helper module for parsing and validating ArchiMate 3.2 Metamodel rules."""

VALID_LAYERS = {"motivation", "strategy", "business", "application", "technology"}

VALID_ELEMENT_TYPES = {
    # Motivation Layer
    "Stakeholder": "motivation",
    "Driver": "motivation",
    "Assessment": "motivation",
    "Goal": "motivation",
    "Outcome": "motivation",
    "Principle": "motivation",
    "Requirement": "motivation",
    "Constraint": "motivation",
    # Strategy Layer
    "Resource": "strategy",
    "Capability": "strategy",
    "CourseOfAction": "strategy",
    "ValueStream": "strategy",
    # Business Layer
    "BusinessActor": "business",
    "BusinessRole": "business",
    "BusinessProcess": "business",
    "BusinessFunction": "business",
    "BusinessService": "business",
    "BusinessInterface": "business",
    "BusinessEvent": "business",
    # Application Layer
    "ApplicationComponent": "application",
    "ApplicationFunction": "application",
    "ApplicationService": "application",
    "ApplicationInterface": "application",
    "DataObject": "application",
    # Technology Layer
    "Node": "technology",
    "Device": "technology",
    "SystemSoftware": "technology",
    "TechnologyService": "technology",
    "TechnologyInterface": "technology",
    "Artifact": "technology",
}

VALID_RELATIONSHIP_TYPES = {
    "Composition",
    "Aggregation",
    "Assignment",
    "Realization",
    "Serving",
    "Access",
    "Influence",
    "Triggering",
    "Flow",
    "Specialization",
    "Association",
}


def is_valid_element_type(element_type: str) -> bool:
    """Check if an element type is a valid ArchiMate 3.2 element."""
    return element_type in VALID_ELEMENT_TYPES


def get_element_layer(element_type: str) -> str | None:
    """Return the ArchiMate layer for a given element type."""
    return VALID_ELEMENT_TYPES.get(element_type)


def is_valid_relationship_type(rel_type: str) -> bool:
    """Check if a relationship type is a valid ArchiMate 3.2 relationship."""
    return rel_type in VALID_RELATIONSHIP_TYPES
