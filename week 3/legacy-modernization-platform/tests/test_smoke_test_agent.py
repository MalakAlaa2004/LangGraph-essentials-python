from agents.smoke_test_agent import build_smoke_test_graph, run_smoke_test_query


def test_graph_structure():
    graph = build_smoke_test_graph()
    assert graph is not None


def test_query_1_valid_relationship():
    query = "Is 'ApplicationComponent serves BusinessProcess' a valid relationship in ArchiMate 3.2?"
    ans = run_smoke_test_query(query)
    assert ans is not None
    assert len(ans) > 0


def test_query_2_element_layer_lookup():
    query = "Which layer does the 'Node' element belong to in ArchiMate 3.2?"
    ans = run_smoke_test_query(query)
    assert ans is not None
    assert len(ans) > 0


def test_query_3_invalid_relationship_rejection():
    query = "Is 'BusinessActor realizes Node' a valid relationship in ArchiMate 3.2?"
    ans = run_smoke_test_query(query)
    assert ans is not None
    assert len(ans) > 0
