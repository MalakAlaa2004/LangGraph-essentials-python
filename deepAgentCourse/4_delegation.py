import sys
import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class DelegationState(TypedDict):
    query: str
    target_analyst: str
    subagent_response: str
    response: str

# Subagent Nodes
def technical_analyst_subagent(state: DelegationState):
    # Focuses on hardware requirements, hosting servers, and specs
    ans = "Technical Specs: Requires 4 vCPUs, 16GB RAM, and HSM validation framework compatibility."
    return {"subagent_response": ans}

def billing_analyst_subagent(state: DelegationState):
    # Focuses on pricing, contracts, and discounts
    ans = "Billing specs: Price is $50,000/year, offering 15% discount for B2B bulk licensing."
    return {"subagent_response": ans}

# Supervisor / Router Node
def supervisor_agent(state: DelegationState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Classify user query: '{state['query']}'
Determine if it is 'technical' or 'billing' request.
Return only the target word."""
    res = llm.invoke(prompt)
    target = res.content.strip().lower()
    val = "technical" if "tech" in target or "server" in target or "specs" in target else "billing"
    return {"target_analyst": val}

def route_to_subagent(state: DelegationState):
    if state["target_analyst"] == "technical":
        return "technical_node"
    return "billing_node"

def compile_final_response(state: DelegationState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""User: {state['query']}
Subagent Output: {state['subagent_response']}
Formulate a professional final reply confirming details."""
    res = llm.invoke(prompt)
    return {"response": res.content}

# Compile Graph
builder = StateGraph(DelegationState)
builder.add_node("supervisor", supervisor_agent)
builder.add_node("technical_node", technical_analyst_subagent)
builder.add_node("billing_node", billing_analyst_subagent)
builder.add_node("compiler", compile_final_response)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route_to_subagent, {
    "technical_node": "technical_node",
    "billing_node": "billing_node"
})
builder.add_edge("technical_node", "compiler")
builder.add_edge("billing_node", "compiler")
builder.add_edge("compiler", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- Module 4: Supervisor & Subagent Delegation ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    # Test Technical Query
    print("\n--- Query 1: Technical Specs ---")
    res1 = graph.invoke({"query": "What are the server specs?", "target_analyst": "", "subagent_response": "", "response": ""})
    print("Routed Analyst:", res1["target_analyst"])
    print("Final Response:", res1["response"])

    # Test Billing Query
    print("\n--- Query 2: Pricing Details ---")
    res2 = graph.invoke({"query": "How much does the package cost?", "target_analyst": "", "subagent_response": "", "response": ""})
    print("Routed Analyst:", res2["target_analyst"])
    print("Final Response:", res2["response"])
