import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agents.business_analyst_agent import BusinessAnalystAgent
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


def test_business_analyst_extraction_and_indexing(tmp_path, db):
    storage_dir = str(tmp_path)
    agent = BusinessAnalystAgent(base_storage_dir=storage_dir)

    sys = repo.create_legacy_system(db, name="system-demo")

    sample_sop = "SOP 201: Standard Operating Procedure for Payment Reconciliation."
    extracted = agent.extract_business_elements(
        system_id=sys.id,
        document_text=sample_sop,
        source_location="docs/sop_201.md",
        db=db,
    )

    assert len(extracted) == 3
    actor_elem = extracted[0]
    assert actor_elem.layer == "business"
    assert actor_elem.archimate_type == "BusinessActor"
    assert len(actor_elem.evidence) > 0
    assert actor_elem.evidence[0].location == "docs/sop_201.md"

    # Verify DB index updated
    indexed = repo.list_model_elements(db, sys.id, layer="business")
    assert len(indexed) == 3
