import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agents.integration_mapper_agent import IntegrationMapperAgent
from agents.schemas.model_element import ModelElement
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


def test_integration_mapper_valid_and_invalid(tmp_path, db):
    storage_dir = str(tmp_path)
    agent = IntegrationMapperAgent(base_storage_dir=storage_dir)

    sys = repo.create_legacy_system(db, name="system-demo")

    elem1 = ModelElement(
        id=f"{sys.id}-comp-1",
        system_id=sys.id,
        layer="application",
        archimate_type="ApplicationComponent",
        name="Monolith Component",
        description="Application monolith component.",
    )

    elem2 = ModelElement(
        id=f"{sys.id}-soft-1",
        system_id=sys.id,
        layer="technology",
        archimate_type="SystemSoftware",
        name="PostgreSQL DB Engine",
        description="PostgreSQL database engine.",
    )

    # 1. Valid relationship
    updated = agent.map_cross_layer_relationship(
        source_element=elem1,
        target_element=elem2,
        relationship_type="Serving",
        description="System software serves component",
        db=db,
    )

    assert updated is not None
    assert len(updated.relationships) == 1
    assert updated.relationships[0].relationship_type == "Serving"

    # 2. Invalid relationship rejection
    invalid_result = agent.map_cross_layer_relationship(
        source_element=elem1,
        target_element=elem2,
        relationship_type="FakeInvalidType",
        description="Invalid relationship",
        db=db,
    )
    assert invalid_result is None
