import sys
import os
from typing import List, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class MockMCPServer:
    def __init__(self):
        self.db = {
            "papers/pqc_migration_guide.txt": "[Source: MCP Server Resource] PQC roadmap: phase 1 (inventory) 2026, phase 2 (gateway software update) 2028.",
            "standards/fips203_spec.txt": "[Source: MCP Server Resource] FIPS 203 details ML-KEM parameter sets (ML-KEM-512, ML-KEM-768, ML-KEM-1024) based on lattice security."
        }
    def get_resource_list(self) -> List[str]:
        return list(self.db.keys())
    def read_resource(self, path: str) -> str:
        return self.db.get(path, "Error: Resource path invalid.")

class MCPState(TypedDict):
    brief: str
    resources: List[str]
    chosen_resource: str
    data: str
    notes: str

mcp_server = MockMCPServer()

def discover_mcp(state: MCPState):
    paths = mcp_server.get_resource_list()
    return {"resources": paths}

def selector_mcp(state: MCPState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Brief: {state['brief']}
Exposed MCP Files: {state['resources']}
Select which file path to retrieve. Return the path name only."""
    res = llm.invoke(prompt)
    chosen = res.content.strip().strip("'").strip('"')
    if chosen not in state["resources"]:
        chosen = state["resources"][0]
    return {"chosen_resource": chosen}

def fetch_mcp(state: MCPState):
    content = mcp_server.read_resource(state["chosen_resource"])
    return {"data": content}

def synthesize_mcp(state: MCPState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Synthesize the MCP data: {state['data']}
Under brief requirements: {state['brief']}"""
    res = llm.invoke(prompt)
    return {"notes": res.content}

# Compile Graph
builder = StateGraph(MCPState)
builder.add_node("discover", discover_mcp)
builder.add_node("select", selector_mcp)
builder.add_node("fetch", fetch_mcp)
builder.add_node("synthesize", synthesize_mcp)

builder.add_edge(START, "discover")
builder.add_edge("discover", "select")
builder.add_edge("select", "fetch")
builder.add_edge("fetch", "synthesize")
builder.add_edge("synthesize", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- LangGraph Research Agent with MCP Server ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    initial_state = {
        "brief": "Study ML-KEM-768 parameter sets in FIPS 203.",
        "resources": [],
        "chosen_resource": "",
        "data": "",
        "notes": ""
    }
    
    res = graph.invoke(initial_state)
    print(f"\nRetrieved Resource: {res['chosen_resource']}")
    print("\nSynthesized Output:")
    print(res["notes"])
