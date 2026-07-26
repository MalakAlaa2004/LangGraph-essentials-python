from agents.tools.git_tools import commit_to_model, open_pull_request


def test_commit_to_model_tool():
    res = commit_to_model.invoke(
        {
            "system_id": "sys-demo",
            "branch_name": "feature-test",
            "commit_message": "Test commit",
        }
    )
    assert "[SUCCESS]" in res
    assert "feature-test" in res


def test_open_pull_request_tool():
    res = open_pull_request.invoke(
        {
            "head_branch": "feature-test",
            "base_branch": "main",
            "title": "PR Title",
            "body": "PR Body",
        }
    )
    assert res["pr_number"] == "42"
    assert "legacy-model-repo" in res["html_url"]
