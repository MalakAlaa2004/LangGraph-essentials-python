import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agents.infra_analyst_agent import InfraAnalystAgent
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


def test_infra_analyst_extraction_and_indexing(tmp_path, db):
    storage_dir = str(tmp_path)
    agent = InfraAnalystAgent(base_storage_dir=storage_dir)

    sys = repo.create_legacy_system(db, name="system-demo")

    sample_iac = "services:\n  db:\n    image: postgres:16-alpine"
    extracted = agent.extract_infra_elements(
        system_id=sys.id,
        iac_content=sample_iac,
        file_path="infrastructure/docker-compose.yaml",
        db=db,
    )

    assert len(extracted) == 3
    node_elem = extracted[0]
    assert node_elem.layer == "technology"
    assert node_elem.archimate_type == "Node"
    assert len(node_elem.evidence) > 0
    assert node_elem.evidence[0].location.startswith(
        "infrastructure/docker-compose.yaml"
    )

    # Verify DB index updated
    indexed = repo.list_model_elements(db, sys.id, layer="technology")
    assert len(indexed) == 3
