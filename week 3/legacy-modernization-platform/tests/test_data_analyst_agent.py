import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agents.data_analyst_agent import DataAnalystAgent
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


def test_data_analyst_extraction_and_indexing(tmp_path, db):
    storage_dir = str(tmp_path)
    agent = DataAnalystAgent(base_storage_dir=storage_dir)

    sys = repo.create_legacy_system(db, name="system-demo")

    sample_sql = "CREATE TABLE users (id INT, email VARCHAR(255));"
    extracted = agent.extract_data_elements(
        system_id=sys.id,
        sql_content=sample_sql,
        file_path="db/schema.sql",
        db=db,
    )

    assert len(extracted) == 2
    data_elem = extracted[0]
    assert data_elem.layer == "application"
    assert data_elem.archimate_type == "DataObject"
    assert len(data_elem.evidence) > 0
    assert data_elem.evidence[0].location.startswith("db/schema.sql")

    # Verify DB index updated
    indexed = repo.list_model_elements(db, sys.id, layer="application")
    assert len(indexed) == 1
