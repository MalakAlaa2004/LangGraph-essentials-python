import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.api import app
from backend.database import get_db
from backend.models import Base

engine = create_engine(
    "sqlite:///./test_api_temp.db", connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_and_list_systems():
    res = client.post(
        "/api/v1/systems", params={"name": "test-sys", "description": "test sys"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "system_id" in data
    assert data["name"] == "test-sys"

    res_list = client.get("/api/v1/systems")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1


def test_github_webhook_pr_merge():
    payload = {
        "action": "closed",
        "number": 12,
        "pull_request": {
            "number": 12,
            "merged": True,
            "head": {"ref": "feature/payment-monolith"},
        },
    }
    res = client.post(
        "/webhooks/github",
        json=payload,
        headers={"x-github-event": "pull_request"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "processed"
    assert res.json()["event"] == "pull_request_merged"
