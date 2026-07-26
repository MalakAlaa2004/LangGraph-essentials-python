import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agents.codebase_analyst_agent import CodebaseAnalystAgent
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


def test_codebase_analyst_extraction_and_indexing(tmp_path, db):
    storage_dir = str(tmp_path)
    agent = CodebaseAnalystAgent(base_storage_dir=storage_dir)

    sys = repo.create_legacy_system(db, name="system-demo")

    sample_code = "class PaymentHandler:\n    def charge(self): pass"
    extracted = agent.extract_codebase_elements(
        system_id=sys.id,
        code_content=sample_code,
        file_path="legacy/payment_handler.py",
        db=db,
    )

    assert len(extracted) == 3
    comp_elem = extracted[0]
    assert comp_elem.layer == "application"
    assert comp_elem.archimate_type == "ApplicationComponent"
    assert len(comp_elem.evidence) > 0
    assert comp_elem.evidence[0].location.startswith("legacy/payment_handler.py")

    # Verify DB index updated
    indexed = repo.list_model_elements(db, sys.id, layer="application")
    assert len(indexed) == 3
