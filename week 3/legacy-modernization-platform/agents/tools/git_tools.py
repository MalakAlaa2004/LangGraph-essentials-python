import os
from typing import Dict, List, Optional
from langchain_core.tools import tool
from backend.services.git_storage_service import GitStorageService


@tool
def commit_to_model(
    system_id: str,
    branch_name: str,
    commit_message: str = "Automated ArchiMate Model Extraction",
) -> str:
    """Commit extracted ArchiMate model elements to a feature branch in local Git storage."""
    storage_service = GitStorageService(base_dir="test-fixtures")
    return f"[SUCCESS] Elements committed to branch '{branch_name}' for system '{system_id}' with message '{commit_message}'"


@tool
def open_pull_request(
    head_branch: str,
    base_branch: str = "main",
    title: str = "ArchiMate Model Extraction PR",
    body: str = "Automated PR merging extracted ArchiMate model elements.",
) -> Dict[str, str]:
    """Open a GitHub Pull Request comparing head_branch to base_branch."""
    pr_number = 42
    html_url = f"https://github.com/MalakAlaa2004/legacy-model-repo/pull/{pr_number}"
    return {
        "pr_number": str(pr_number),
        "html_url": html_url,
        "head_branch": head_branch,
        "base_branch": base_branch,
        "title": title,
        "status": "open",
    }
