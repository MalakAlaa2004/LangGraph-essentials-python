import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agents.reconciler_agent import ReconcilerAgent
from agents.schemas.model_element import EvidenceCitation, ModelElement
from backend.models import Base
from backend.repository import system_repository as repo


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_reconciler_deduplication(tmp_path, db):
    storage_dir = str(tmp_path)
    agent = ReconcilerAgent(base_storage_dir=storage_dir)

    sys = repo.create_legacy_system(db, name="system-demo")

    ev1 = EvidenceCitation(
        source_type="code",
        location="app1.py#L1-L10",
        excerpt="code 1",
        confidence_score=0.9,
    )
    ev2 = EvidenceCitation(
        source_type="doc",
        location="doc2.md#L15-L20",
        excerpt="doc 2",
        confidence_score=0.85,
    )

    elem1 = ModelElement(
        id=f"{sys.id}-comp-1",
        system_id=sys.id,
        layer="application",
        archimate_type="ApplicationComponent",
        name="Payment Monolith",
        description="First component",
        evidence=[ev1],
    )
    elem2 = ModelElement(
        id=f"{sys.id}-comp-dup",
        system_id=sys.id,
        layer="application",
        archimate_type="ApplicationComponent",
        name="Payment Monolith",
        description="Duplicate component",
        evidence=[ev2],
    )

    reconciled = agent.reconcile_elements([elem1, elem2], db=db)
    assert len(reconciled) == 1
    merged = reconciled[0]
    assert merged.name == "Payment Monolith"
    assert len(merged.evidence) == 2
