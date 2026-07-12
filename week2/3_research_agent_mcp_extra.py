import sys
import os
from typing import List, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class StandardMCPServer:
    def __init__(self):
        self.db = {"standards/fips203.txt": "[NIST Standards Server] ML-KEM lattice-based key encapsulation specifications."}
    def list_paths(self): return list(self.db.keys())
    def read_path(self, path): return self.db.get(path, "")

class BankingMCPServer:
    def __init__(self):
        self.db = {"banking/swift_pqc.txt": "[Banking Server] SWIFT gateway transition cost timeline analysis."}
    def list_paths(self): return list(self.db.keys())
    def read_path(self, path): return self.db.get(path, "")

class MCPExtraState(TypedDict):
    brief: str
    target_domain: str
    resources: List[str]
    chosen_resource: str
    data: str
    notes: str

standards_server = StandardMCPServer()
banking_server = BankingMCPServer()

def classify_mcp_domain(state: MCPExtraState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Classify which database domain this brief belongs to: 'standards' (for algorithms) or 'banking' (for timelines/costs).
Brief: {state['brief']}
Return ONLY 'standards' or 'banking'."""
    res = llm.invoke(prompt)
    domain = res.content.strip().lower()
    if domain not in ["standards", "banking"]:
        domain = "standards"
    return {"target_domain": domain}

def discover_mcp(state: MCPExtraState):
    if state["target_domain"] == "standards":
        paths = standards_server.list_paths()
    else:
        paths = banking_server.list_paths()
    return {"resources": paths}

def selector_mcp(state: MCPExtraState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Brief: {state['brief']}
MCP Resources: {state['resources']}
Select the file. Return path name only."""
    res = llm.invoke(prompt)
    chosen = res.content.strip().strip("'").strip('"')
    if chosen not in state["resources"]:
        chosen = state["resources"][0]
    return {"chosen_resource": chosen}

def fetch_mcp(state: MCPExtraState):
    if state["target_domain"] == "standards":
        content = standards_server.read_path(state["chosen_resource"])
    else:
        content = banking_server.read_path(state["chosen_resource"])
    return {"data": content}

def synthesize_mcp(state: MCPExtraState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Synthesize the MCP data: {state['data']}
Brief: {state['brief']}"""
    res = llm.invoke(prompt)
    return {"notes": res.content}

# Compile Graph
builder = StateGraph(MCPExtraState)
builder.add_node("classify", classify_mcp_domain)
builder.add_node("discover", discover_mcp)
builder.add_node("select", selector_mcp)
builder.add_node("fetch", fetch_mcp)
builder.add_node("synthesize", synthesize_mcp)

builder.add_edge(START, "classify")
builder.add_edge("classify", "discover")
builder.add_edge("discover", "select")
builder.add_edge("select", "fetch")
builder.add_edge("fetch", "synthesize")
builder.add_edge("synthesize", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- Extra Multi-Server MCP Router ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    print("\n--- Executing Timelines Query ---")
    initial_state = {
        "brief": "SWIFT gateway transition costs timeline",
        "target_domain": "",
        "resources": [],
        "chosen_resource": "",
        "data": "",
        "notes": ""
    }
    res = graph.invoke(initial_state)
    print(f"Server Target Domain: {res['target_domain']}")
    print(f"Retrieved Path: {res['chosen_resource']}")
    print("Output Notes:", res["notes"])
