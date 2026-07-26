import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agents.strategy_analyst_agent import StrategyAnalystAgent
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


def test_strategy_analyst_extraction_and_indexing(tmp_path, db):
    storage_dir = str(tmp_path)
    agent = StrategyAnalystAgent(base_storage_dir=storage_dir)

    # Pre-create system in DB
    sys = repo.create_legacy_system(db, name="system-demo")

    sample_doc = "ADR 002: Upgrade security compliance to PCI-DSS v4.0."
    extracted = agent.extract_strategy_elements(
        system_id=sys.id,
        document_text=sample_doc,
        source_location="docs/adr_002.md",
        db=db,
    )

    assert len(extracted) == 2
    goal_elem = extracted[0]
    assert goal_elem.layer in ["motivation", "strategy"]
    assert len(goal_elem.evidence) > 0
    assert goal_elem.evidence[0].location == "docs/adr_002.md"

    # Verify DB index updated
    indexed = repo.list_model_elements(db, sys.id)
    assert len(indexed) == 2
