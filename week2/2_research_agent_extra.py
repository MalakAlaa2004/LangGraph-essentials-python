import sys
import os
import json
from typing import List, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class ResearchState(TypedDict):
    brief: str
    current_query: str
    queries: List[str]
    search_results: str
    notes: str
    gap_critique: str
    iteration: int

def mock_search(query: str) -> str:
    q = query.lower()
    if "nist" in q or "fips" in q:
        return "[Source: NIST] FIPS 203 defines ML-KEM. FIPS 204 defines ML-DSA."
    elif "cost" in q or "budget" in q:
        return "[Source: Gartner] Interbank software updates cost $2.4B globally."
    else:
        return f"[Source: General Database] Search facts for query: {query}"

def planner(state: ResearchState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Brief: {state['brief']}
Gap Critique: {state['gap_critique']}
Formulate a query to run. Return ONLY the search query."""
    res = llm.invoke(prompt)
    return {"current_query": res.content}

def search(state: ResearchState):
    results = mock_search(state["current_query"])
    return {
        "search_results": results,
        "queries": state["queries"] + [state["current_query"]]
    }

def synthesize(state: ResearchState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Add findings: {state['search_results']}
To current notes: {state['notes']}"""
    res = llm.invoke(prompt)
    return {"notes": res.content}

def gaps_detector(state: ResearchState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Brief: {state['brief']}
Notes: {state['notes']}
Evaluate if the notes satisfy all parameters of the brief. If not, state what is missing.
Return JSON format: {{"has_gaps": true/false, "gap_description": "gaps description"}}"""
    res = llm.invoke(prompt)
    try:
        data = json.loads(res.content)
        has_gaps = data["has_gaps"]
        gap_description = data["gap_description"]
    except:
        has_gaps = state["iteration"] < 1
        gap_description = "Missing technical migration budget details." if has_gaps else ""

    return {
        "gap_critique": gap_description,
        "iteration": state["iteration"] + 1
    }

def route_critique(state: ResearchState):
    if state["gap_critique"] and state["iteration"] < 3:
        print(f"\n[Self-Critique Gap Detected]: {state['gap_critique']}")
        return "plan"
    return END

# Compile Graph
builder = StateGraph(ResearchState)
builder.add_node("plan", planner)
builder.add_node("search", search)
builder.add_node("synthesize", synthesize)
builder.add_node("gaps_detector", gaps_detector)

builder.add_edge(START, "plan")
builder.add_edge("plan", "search")
builder.add_edge("search", "synthesize")
builder.add_edge("synthesize", "gaps_detector")
builder.add_conditional_edges("gaps_detector", route_critique, {
    "plan": "plan",
    END: END
})

graph = builder.compile()

if __name__ == "__main__":
    print("--- Extra Research Agent with Self-Critique / Loop Correction ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    initial_state = {
        "brief": "Assess technical specifications (FIPS 203) and migration costs for interbank gateways.",
        "current_query": "",
        "queries": [],
        "search_results": "",
        "notes": "Initial base notes.",
        "gap_critique": "",
        "iteration": 0
    }
    
    res = graph.invoke(initial_state)
    print("\nFinal Queries Executed:", res["queries"])
    print("\nFinal Self-Corrected Research Notes:")
    print(res["notes"])
