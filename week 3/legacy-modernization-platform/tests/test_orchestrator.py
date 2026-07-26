from agents.orchestrator import build_phase1_orchestrator, run_orchestration


def test_orchestrator_structure():
    orchestrator = build_phase1_orchestrator()
    assert orchestrator is not None


def test_orchestrator_execution():
    res = run_orchestration("system-demo")
    assert res is not None
    assert res["system_id"] == "system-demo"
    assert len(res["steps_completed"]) == 7
    assert res["steps_completed"] == [
        "strategy_analyst",
        "business_analyst",
        "codebase_analyst",
        "infra_analyst",
        "data_analyst",
        "reconciler",
        "validator",
    ]
