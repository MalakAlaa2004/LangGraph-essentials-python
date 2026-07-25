import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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


def test_legacy_system_crud(db):
    sys = repo.create_legacy_system(
        db, name="PaymentGateway", description="Legacy payment processing monolith"
    )
    assert sys.id.startswith("sys-")
    assert sys.name == "PaymentGateway"

    fetched = repo.get_legacy_system(db, sys.id)
    assert fetched is not None
    assert fetched.name == "PaymentGateway"

    all_systems = repo.list_legacy_systems(db)
    assert len(all_systems) == 1


def test_model_element_index_upsert_idempotency(db):
    sys = repo.create_legacy_system(db, name="OrderService")

    # Insert element
    elem = repo.upsert_model_element_index(
        db,
        element_id="elem-1",
        system_id=sys.id,
        layer="application",
        archimate_type="ApplicationComponent",
        name="OrderProcessor",
        git_path="systems/sys-1/as-is/application/elem-1.json",
        current_commit="sha123",
    )
    assert elem.name == "OrderProcessor"

    # Update element idempotently
    elem_updated = repo.upsert_model_element_index(
        db,
        element_id="elem-1",
        system_id=sys.id,
        layer="application",
        archimate_type="ApplicationComponent",
        name="OrderProcessorV2",
        git_path="systems/sys-1/as-is/application/elem-1.json",
        current_commit="sha456",
    )
    assert elem_updated.name == "OrderProcessorV2"
    assert len(repo.list_model_elements(db, sys.id)) == 1


def test_job_status_update_idempotency(db):
    sys = repo.create_legacy_system(db, name="AuthSystem")
    job = repo.create_job(db, system_id=sys.id, phase="as-is")
    assert job.status == "queued"

    # Update status to failed
    updated_1 = repo.update_job_status(
        db, job.id, status="failed", error_message="Syntax error in IaC"
    )
    assert updated_1.status == "failed"

    # Call status update twice with same arguments (Idempotency Test)
    updated_2 = repo.update_job_status(
        db, job.id, status="failed", error_message="Syntax error in IaC"
    )
    assert updated_2.status == "failed"
    assert updated_2.finished_at is not None


def test_artifact_version_crud(db):
    sys = repo.create_legacy_system(db, name="InventoryApp")
    ver = repo.create_artifact_version(
        db,
        system_id=sys.id,
        commit_sha="commit123",
        tag="as-is/v1",
        author_type="agent",
        run_id="run-xyz",
    )
    assert ver.approval_status == "pending"

    # Update status to approved
    approved = repo.update_artifact_version_status(
        db, ver.id, approval_status="approved", approved_by="admin@client.gov"
    )
    assert approved.approval_status == "approved"
    assert approved.approved_by == "admin@client.gov"


def test_evidence_sources_crud(db):
    sys = repo.create_legacy_system(db, name="CRM")
    src = repo.create_evidence_source(
        db, system_id=sys.id, source_type="code", location="/evidence/code/main.py"
    )
    assert src.location == "/evidence/code/main.py"
    assert len(repo.list_evidence_sources(db, sys.id)) == 1
