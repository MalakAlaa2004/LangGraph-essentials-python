import sys
import os
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
    iteration: int

def mock_search(query: str) -> str:
    q = query.lower()
    if "nist" in q or "fips" in q:
        return "[Source: NIST Cryptographic Standards 2024] FIPS 203 details ML-KEM for secure key exchange, while FIPS 204 defines ML-DSA digital signatures."
    elif "timeline" in q or "cost" in q:
        return "[Source: Banking PQC Report] Total cost of gateway software updates is estimated at $2.4B globally, with compliance deadlines setting targets between 2028 and 2031."
    else:
        return f"[Source: General Search] Information on PQC research query: {query}."

def query_planner(state: ResearchState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Review the research brief: '{state['brief']}'
Notes so far: '{state['notes']}'
Formulate the next search query. Return ONLY the search query text."""
    res = llm.invoke(prompt)
    return {"current_query": res.content}

def search_executor(state: ResearchState):
    query = state["current_query"]
    results = mock_search(query)
    return {
        "search_results": results,
        "queries": state["queries"] + [query]
    }

def synthesize_notes(state: ResearchState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Incorporate this new finding:\n{state['search_results']}\ninto our current research notes:\n{state['notes']}\nDraft the updated research summary."""
    res = llm.invoke(prompt)
    return {
        "notes": res.content,
        "iteration": state["iteration"] + 1
    }

def check_loop(state: ResearchState):
    if state["iteration"] >= 2:
        return END
    return "plan"

# Compile Graph
builder = StateGraph(ResearchState)
builder.add_node("plan", query_planner)
builder.add_node("search", search_executor)
builder.add_node("synthesize", synthesize_notes)

builder.add_edge(START, "plan")
builder.add_edge("plan", "search")
builder.add_edge("search", "synthesize")
builder.add_conditional_edges("synthesize", check_loop, {
    "plan": "plan",
    END: END
})

graph = builder.compile()

if __name__ == "__main__":
    print("--- LangGraph Research Agent Architecture ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    initial_state = {
        "brief": "Analyze FIPS 203 standards and financial timelines for PQC migration.",
        "current_query": "",
        "queries": [],
        "search_results": "",
        "notes": "Base notes: Migration starting.",
        "iteration": 0
    }
    
    print("\n--- Executing Research Agent Loop ---")
    res = graph.invoke(initial_state)
    print("\nSearch Queries Run:", res["queries"])
    print("\nFinal Research Notes:")
    print(res["notes"])
