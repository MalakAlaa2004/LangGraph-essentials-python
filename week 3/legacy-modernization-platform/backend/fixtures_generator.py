import os
import shutil
from typing import List
from agents.schemas.model_element import EvidenceCitation, ModelElement, Relationship


def create_synthetic_elements(system_id: str) -> List[ModelElement]:
    """Build 12 synthetic ArchiMate 3.2 elements across all 5 layers."""

    # Common Evidence Citation
    code_evidence = EvidenceCitation(
        source_type="code",
        location="legacy/payment_processor.py#L15-L85",
        excerpt="class LegacyPaymentMonolith:\n    def process_payment(self, payload):",
        confidence_score=0.95,
        rationales=["Monolith payment handling class located in legacy codebase"],
    )

    iac_evidence = EvidenceCitation(
        source_type="iac",
        location="infrastructure/docker-compose.yaml#L10-L30",
        excerpt="services:\n  postgres:\n    image: postgres:16-alpine",
        confidence_score=0.98,
        rationales=["PostgreSQL database container declared in IaC"],
    )

    elements = [
        # --- 1. MOTIVATION LAYER ---
        ModelElement(
            id="goal-001",
            system_id=system_id,
            layer="motivation",
            archimate_type="Goal",
            name="Reduce Payment Latency",
            description="Achieve sub-200ms transaction settlement latency across all merchant gateways.",
            properties={"priority": "high", "target_ms": 200},
            evidence=[code_evidence],
        ),
        ModelElement(
            id="req-001",
            system_id=system_id,
            layer="motivation",
            archimate_type="Requirement",
            name="Decompose Payment Monolith",
            description="Break payment monolith into microservices for independent scaling.",
            properties={"compliance": "PCI-DSS v4.0"},
            relationships=[
                Relationship(
                    target_element_id="goal-001",
                    relationship_type="Realization",
                    description="Fulfills latency goal",
                )
            ],
            evidence=[code_evidence],
        ),
        # --- 2. STRATEGY LAYER ---
        ModelElement(
            id="cap-001",
            system_id=system_id,
            layer="strategy",
            archimate_type="Capability",
            name="Real-time Settlement Capability",
            description="Ability to process and verify electronic transactions instantaneously.",
            properties={"availability_sla": "99.99%"},
            relationships=[
                Relationship(
                    target_element_id="goal-001",
                    relationship_type="Realization",
                    description="Realizes strategic goal",
                )
            ],
            evidence=[code_evidence],
        ),
        # --- 3. BUSINESS LAYER ---
        ModelElement(
            id="actor-001",
            system_id=system_id,
            layer="business",
            archimate_type="BusinessActor",
            name="E-Commerce Merchant",
            description="External client integrating with the payment processing platform.",
            properties={"client_type": "enterprise"},
            evidence=[code_evidence],
        ),
        ModelElement(
            id="role-001",
            system_id=system_id,
            layer="business",
            archimate_type="BusinessRole",
            name="Payment Settlement Officer",
            description="Internal role managing daily clearing and reconciliation batches.",
            properties={"department": "finance"},
            evidence=[code_evidence],
        ),
        ModelElement(
            id="proc-001",
            system_id=system_id,
            layer="business",
            archimate_type="BusinessProcess",
            name="Process Credit Card Payment",
            description="End-to-end business workflow verifying merchant credentials and settling funds.",
            properties={"avg_duration_sec": 1.2},
            relationships=[
                Relationship(
                    target_element_id="role-001",
                    relationship_type="Assignment",
                    description="Role executes process",
                )
            ],
            evidence=[code_evidence],
        ),
        # --- 4. APPLICATION LAYER ---
        ModelElement(
            id="comp-001",
            system_id=system_id,
            layer="application",
            archimate_type="ApplicationComponent",
            name="Legacy Payment Monolith",
            description="Monolithic Python/Django application handling authentication, processing, and logging.",
            properties={"tech_stack": "python3.8/django2.2", "loc": 45000},
            relationships=[
                Relationship(
                    target_element_id="data-001",
                    relationship_type="Access",
                    description="Reads and writes transaction payload",
                )
            ],
            evidence=[code_evidence],
        ),
        ModelElement(
            id="appsvc-001",
            system_id=system_id,
            layer="application",
            archimate_type="ApplicationService",
            name="Credit Card Processing Service",
            description="Exposed application service accepting credit card tokenization requests.",
            properties={"protocol": "REST/JSON"},
            relationships=[
                Relationship(
                    target_element_id="proc-001",
                    relationship_type="Serving",
                    description="Services business payment process",
                )
            ],
            evidence=[code_evidence],
        ),
        ModelElement(
            id="data-001",
            system_id=system_id,
            layer="application",
            archimate_type="DataObject",
            name="Transaction Record Payload",
            description="Data object containing payment token, amount, currency, and timestamp.",
            properties={"schema_version": "v1.2"},
            evidence=[code_evidence],
        ),
        # --- 5. TECHNOLOGY LAYER ---
        ModelElement(
            id="node-001",
            system_id=system_id,
            layer="technology",
            archimate_type="Node",
            name="On-Premises Linux Host",
            description="Ubuntu Linux 20.04 physical host executing Docker containers.",
            properties={"os": "Ubuntu 20.04 LTS", "ram_gb": 64},
            evidence=[iac_evidence],
        ),
        ModelElement(
            id="software-001",
            system_id=system_id,
            layer="technology",
            archimate_type="SystemSoftware",
            name="PostgreSQL Database Engine",
            description="Relational database engine storing persistent application state.",
            properties={"version": "PostgreSQL 16 Alpine"},
            relationships=[
                Relationship(
                    target_element_id="comp-001",
                    relationship_type="Serving",
                    description="Provides relational storage to monolith",
                )
            ],
            evidence=[iac_evidence],
        ),
        ModelElement(
            id="artifact-001",
            system_id=system_id,
            layer="technology",
            archimate_type="Artifact",
            name="Database Schema SQL Migration Script",
            description="SQL DDL script initializing database tables and foreign keys.",
            properties={"file_format": "sql"},
            relationships=[
                Relationship(
                    target_element_id="software-001",
                    relationship_type="Realization",
                    description="Realizes DB schema",
                )
            ],
            evidence=[iac_evidence],
        ),
    ]

    return elements


def generate_fixtures(
    output_dir: str, system_id: str = "system-demo", phase: str = "as-is"
) -> List[str]:
    """Generate synthetic ArchiMate JSON fixture files across all 5 layers."""
    elements = create_synthetic_elements(system_id)
    created_files = []

    base_path = os.path.join(output_dir, "systems", system_id, phase)
    if os.path.exists(base_path):
        shutil.rmtree(base_path)

    for element in elements:
        layer_dir = os.path.join(base_path, element.layer)
        os.makedirs(layer_dir, exist_ok=True)
        file_path = os.path.join(layer_dir, f"{element.id}.json")

        # Validate JSON serialization & re-parse validation
        json_data = element.model_dump_json(indent=2)
        ModelElement.model_validate_json(json_data)  # Self-check validation

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_data)
        created_files.append(file_path)

    print(
        f"[SUCCESS] Generated {len(created_files)} synthetic ArchiMate fixture files at: {base_path}"
    )
    return created_files


if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    fixtures_dir = os.path.join(project_root, "test-fixtures")
    generate_fixtures(fixtures_dir)
