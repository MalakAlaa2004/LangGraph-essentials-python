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

class SalesAssistantState(TypedDict):
    customer_query: str
    inventory_checked: bool
    quote_calculated: float
    manager_approved: bool
    response: str
    logs: List[str]

def crm_inventory_check(state: SalesAssistantState):
    # Simulated stock check
    return {
        "inventory_checked": True,
        "logs": state["logs"] + ["CRM Inventory Check completed (Stock available)."]
    }

def calculate_quote(state: SalesAssistantState):
    # Calculated 15% discount on $50,000
    total = 50000.0 * 0.85
    return {
        "quote_calculated": total,
        "logs": state["logs"] + [f"Sales quote calculated: ${total}"]
    }

def sales_manager_checkpoint(state: SalesAssistantState):
    # Interrupt node
    return {
        "logs": state["logs"] + ["Awaiting Manager approval for pricing override."]
    }

def finalize_sales_contract(state: SalesAssistantState):
    if state["manager_approved"]:
        res = f"Invoice compiled. Total: ${state['quote_calculated']}. Contract is ready to sign."
        log = "Contract generated successfully."
    else:
        res = "Contract rejected due to pricing policies."
        log = "Contract execution aborted."
    return {
        "response": res,
        "logs": state["logs"] + [log]
    }

# Assemble Graph
builder = StateGraph(SalesAssistantState)
builder.add_node("crm_check", crm_inventory_check)
builder.add_node("calculate", calculate_quote)
builder.add_node("approval_gate", sales_manager_checkpoint)
builder.add_node("finalize", finalize_sales_contract)

builder.add_edge(START, "crm_check")
builder.add_edge("crm_check", "calculate")
builder.add_edge("calculate", "approval_gate")
builder.add_edge("approval_gate", "finalize")
builder.add_edge("finalize", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["finalize"])

if __name__ == "__main__":
    print("--- Module 5: Complete B2B Tech Sales Assistant System ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    thread = {"configurable": {"thread_id": "b2b-deal-45"}}
    initial_state = {
        "customer_query": "Quote requested for Enterprise Cloud Suite.",
        "inventory_checked": False,
        "quote_calculated": 0.0,
        "manager_approved": False,
        "response": "",
        "logs": []
    }
    
    # Run pipeline up to finalize interrupt
    graph.invoke(initial_state, thread)
    print("\nExecution logs before interrupt:")
    for log in graph.get_state(thread).values["logs"]:
        print(f" - {log}")
    print("\nDeal is paused. Awaiting manager validation...")

    # Manager approves deal
    print("\n--- Sales Manager approves quote override & Resumes Graph ---")
    graph.update_state(thread, {"manager_approved": True})
    res = graph.invoke(None, thread)
    print("\nFinal Output:", res["response"])
    print("Final Execution log:", res["logs"][-1])
