from agents.multi_agent_pipeline import (
    build_multi_agent_pipeline,
    run_pipeline,
)


def test_pipeline_graph_structure():
    pipeline = build_multi_agent_pipeline()
    assert pipeline is not None


def test_full_pipeline_execution():
    result = run_pipeline("system-demo")
    assert result is not None
    assert len(result["processed_layers"]) == 5
    assert result["processed_layers"] == [
        "motivation",
        "strategy",
        "business",
        "application",
        "technology",
    ]
    assert result["elements_count"] == 12
