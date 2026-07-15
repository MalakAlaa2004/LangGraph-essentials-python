import sys
import os
import json
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class DeepAgentState(TypedDict):
    input: str
    mcp_resources: List[str]
    read_data: str
    response: str

# Simulated Model Context Protocol (MCP) Server for CRM data
class MockCRMMcpServer:
    def list_resources(self) -> List[str]:
        return ["crm/leads_database.csv", "crm/deal_templates.json"]
        
    def read_resource(self, path: str) -> str:
        if path == "crm/leads_database.csv":
            return "LeadID,Company,Contact,DealValue\nL01,Acme Corp,John Doe,$50000\nL02,Stark Industries,Pepper Potts,$120000"
        return "Template not found."

crm_server = MockCRMMcpServer()

# Nodes
def list_crm_resources(state: DeepAgentState):
    resources = crm_server.list_resources()
    return {"mcp_resources": resources}

def fetch_crm_lead(state: DeepAgentState):
    # Agent decides to read the lead database
    target = "crm/leads_database.csv"
    data = crm_server.read_resource(target)
    return {"read_data": data}

def compose_response(state: DeepAgentState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Generate a sales follow-up email.
Customer Context: {state['input']}
CRM Database Record:
{state['read_data']}
Keep it concise."""
    res = llm.invoke(prompt)
    return {"response": res.content}

# Compile Graph
builder = StateGraph(DeepAgentState)
builder.add_node("list_mcp", list_crm_resources)
builder.add_node("fetch_mcp", fetch_crm_lead)
builder.add_node("compose", compose_response)

builder.add_edge(START, "list_mcp")
builder.add_edge("list_mcp", "fetch_mcp")
builder.add_edge("fetch_mcp", "compose")
builder.add_edge("compose", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- Module 1 Extra: MCP Connected Deep Sales Agent ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    initial_state = {
        "input": "Follow up with Stark Industries regarding their deal status.",
        "mcp_resources": [],
        "read_data": "",
        "response": ""
    }
    res = graph.invoke(initial_state)
    print("\nDiscovered MCP Resources:", res["mcp_resources"])
    print("\nCRM Fetched Record:\n", res["read_data"])
    print("\nGenerated Email:\n", res["response"])
