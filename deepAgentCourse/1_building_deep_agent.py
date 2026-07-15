import sys
import os
import json
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class SalesState(TypedDict):
    customer_query: str
    discount_requested: float
    discount_approved: bool
    agent_response: str
    logs: List[str]

# Tool
def check_inventory(product_name: str) -> str:
    return f"Product '{product_name}' is in stock (25 units available)."

def sales_agent(state: SalesState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    system_prompt = """You are a B2B Tech Sales Assistant. Answer the customer's query.
You have access to check_inventory tool.
If they ask for a discount, note it in state but do not approve it yourself.
Your output must be professional."""
    
    # Simple check for inventory tool trigger
    if "stock" in state["customer_query"].lower() or "available" in state["customer_query"].lower():
        tool_res = check_inventory("Enterprise Cloud Suite")
        log = f"Agent tool call: check_inventory -> {tool_res}"
    else:
        log = "Agent evaluated query without tools."
        
    prompt = f"{system_prompt}\nCustomer: {state['customer_query']}"
    res = llm.invoke(prompt)
    
    return {
        "agent_response": res.content,
        "logs": state["logs"] + [log]
    }

def approval_check(state: SalesState):
    # This node executes after interrupt for manager approval
    if state["discount_approved"]:
        log = f"Discount of {state['discount_requested']}% was APPROVED by Manager."
        res = f"Good news! Your discount request of {state['discount_requested']}% has been approved."
    else:
        log = f"Discount of {state['discount_requested']}% was REJECTED by Manager."
        res = "Unfortunately, we cannot offer the requested discount at this time."
    return {
        "agent_response": res,
        "logs": state["logs"] + [log]
    }

# Build graph
builder = StateGraph(SalesState)
builder.add_node("agent", sales_agent)
builder.add_node("manager_approval", approval_check)

builder.add_edge(START, "agent")
builder.add_edge("agent", "manager_approval")
builder.add_edge("manager_approval", END)

memory = MemorySaver()
# Interrupt before manager approval if discount is requested
graph = builder.compile(checkpointer=memory, interrupt_before=["manager_approval"])

if __name__ == "__main__":
    print("--- Module 1: Building a Deep Agent (Sales Assistant Core) ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    thread = {"configurable": {"thread_id": "sales-session-1"}}
    initial_state = {
        "customer_query": "I want to purchase the Enterprise Cloud Suite but need a 15% discount.",
        "discount_requested": 15.0,
        "discount_approved": False,
        "agent_response": "",
        "logs": []
    }
    
    # Run agent: will interrupt before manager_approval
    graph.invoke(initial_state, thread)
    print("\n[Graph Paused] Awaiting Manager Approval...")
    
    # Approve discount & Resume
    print("\n--- Sales Manager Approves Discount & Resumes Graph ---")
    graph.update_state(thread, {"discount_approved": True})
    res = graph.invoke(None, thread)
    print("Final Agent Response:", res["agent_response"])
