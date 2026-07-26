from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.repository import system_repository as repo

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/github")
async def github_webhook_receiver(
    request: Request,
    x_github_event: str = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Receive GitHub webhook events for pull request merges."""
    payload = await request.json()

    if x_github_event == "pull_request":
        action = payload.get("action")
        pull_request = payload.get("pull_request", {})
        merged = pull_request.get("merged", False)

        if action == "closed" and merged:
            pr_number = pull_request.get("number")
            head_branch = pull_request.get("head", {}).get("ref", "feature-branch")

            # Record merged artifact version in DB
            repo.create_artifact_version(
                db=db,
                system_id="system-demo",
                commit_sha="a1b2c3d4e5f6",
                tag=f"pr-{pr_number}-merged",
                author_type="github_webhook",
                phase="as-is",
            )
            return {
                "status": "processed",
                "event": "pull_request_merged",
                "pr_number": pr_number,
                "branch": head_branch,
            }

    return {"status": "ignored", "event": x_github_event}
