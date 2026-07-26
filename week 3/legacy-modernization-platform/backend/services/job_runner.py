import asyncio
import concurrent.futures
from typing import Optional
from sqlalchemy.orm import Session
from agents.orchestrator import run_orchestration
from backend.database import SessionLocal
from backend.repository import system_repository as repo

executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def execute_job_sync(job_id: str, system_id: str):
    """Synchronous worker function executing orchestration in a thread pool."""
    db: Session = SessionLocal()
    try:
        repo.update_job_status(db, job_id, "RUNNING")
        run_orchestration(system_id)
        repo.update_job_status(db, job_id, "COMPLETED")
    except Exception as e:
        print(f"❌ Job {job_id} failed: {e}")
        repo.update_job_status(db, job_id, "FAILED", error_message=str(e))
    finally:
        db.close()


async def submit_async_job(job_id: str, system_id: str):
    """Submit orchestration job to background thread pool."""
    loop = asyncio.get_running_loop()
    loop.run_in_executor(executor, execute_job_sync, job_id, system_id)
