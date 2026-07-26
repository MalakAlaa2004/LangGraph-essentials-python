import os
from typing import Any, Dict, List
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.repository import system_repository as repo
from backend.services.job_runner import submit_async_job
from backend.webhooks.github_webhook import router as github_webhook_router

app = FastAPI(
    title="Legacy Modernization Platform REST API",
    description="Backend REST API for ArchiMate model extraction and multi-agent orchestration.",
    version="1.0.0",
)

app.include_router(github_webhook_router)

# Mount Frontend Web Dashboard
frontend_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
def read_root():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Legacy Modernization Platform Backend API"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "legacy-modernization-platform"}


@app.post("/api/v1/systems")
def create_system(name: str, description: str = "", db: Session = Depends(get_db)):
    sys = repo.create_legacy_system(db, name=name, description=description)
    return {"system_id": sys.id, "name": sys.name, "created_at": sys.created_at}


@app.get("/api/v1/systems")
def list_systems(db: Session = Depends(get_db)):
    systems = repo.list_legacy_systems(db)
    return [{"id": s.id, "name": s.name, "description": s.description} for s in systems]


@app.post("/api/v1/jobs")
async def trigger_job(
    system_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    sys = repo.get_legacy_system(db, system_id)
    if not sys:
        raise HTTPException(status_code=404, detail="Legacy system not found")

    job = repo.create_job(db, system_id=system_id, job_type="ingestion_pipeline")
    background_tasks.add_task(submit_async_job, job.id, system_id)

    return {
        "job_id": job.id,
        "system_id": system_id,
        "status": job.status,
        "job_type": job.job_type,
    }


@app.get("/api/v1/jobs/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = repo.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.id,
        "system_id": job.system_id,
        "status": job.status,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


@app.get("/api/v1/elements/{system_id}")
def get_model_elements(system_id: str, db: Session = Depends(get_db)):
    elements = repo.list_model_elements(db, system_id=system_id)
    return [
        {
            "id": e.id,
            "layer": e.layer,
            "archimate_type": e.archimate_type,
            "name": e.name,
            "git_path": e.git_path,
        }
        for e in elements
    ]
