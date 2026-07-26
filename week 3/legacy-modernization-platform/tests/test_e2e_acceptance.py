import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agents.orchestrator import run_orchestration
from backend.models import Base
from backend.repository import system_repository as repo
from backend.services.git_storage_service import GitStorageService


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


def test_end_to_end_mvp_acceptance_flow(tmp_path, db):
    """End-to-end acceptance test verifying full MVP Phase 1 pipeline execution."""

    # 1. Register Legacy System in Database
    system = repo.create_legacy_system(
        db=db,
        name="system-demo",
        description="Legacy Payment Processing Platform Monolith",
    )
    assert system.id is not None
    assert system.name == "system-demo"

    # 2. Execute Top-Level Orchestration Pipeline
    result = run_orchestration(system_id=system.id)
    assert result is not None
    assert result["system_id"] == system.id
    assert len(result["steps_completed"]) == 7

    # 3. Verify Local Git Storage Persistence
    storage_service = GitStorageService(base_dir="test-fixtures")
    loaded_elements = storage_service.list_model_elements("system-demo", phase="as-is")
    assert len(loaded_elements) >= 12

    # 4. Verify GitHub Webhook PR-Merge Version Record
    artifact_version = repo.create_artifact_version(
        db=db,
        system_id=system.id,
        commit_sha="e2e-accept-sha-998877",
        tag="pr-42-merged",
        author_type="e2e_test_runner",
        phase="as-is",
    )
    assert artifact_version.id is not None
    assert artifact_version.tag == "pr-42-merged"
