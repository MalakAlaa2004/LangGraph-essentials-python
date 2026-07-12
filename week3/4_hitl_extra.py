import sys
import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

class HitlExtraState(TypedDict):
    command: str
    target_device: str
    auth_decision: str # 'Approved', 'Rejected', or 'Modified'
    modified_params: str
    status: str

def security_audit(state: HitlExtraState):
    print(f"\n[Security Audit Log]: Alert! Secure Command: '{state['command']}'")
    return {"status": "Pending Human Audit"}

def route_approval(state: HitlExtraState):
    """Extra Concept: Multi-Path Human Override Routing."""
    decision = state.get("auth_decision", "Rejected")
    if decision == "Approved":
        return "execute"
    elif decision == "Modified":
        return "modify"
    else:
        return "reject"

def execute_action(state: HitlExtraState):
    return {"status": "Action Executed successfully."}

def modify_action(state: HitlExtraState):
    return {"status": f"Action Executed with safe modifications: {state['modified_params']}"}

def reject_action(state: HitlExtraState):
    return {"status": "Action Blocked by Security Protocol."}

# Compile Graph
builder = StateGraph(HitlExtraState)
builder.add_node("audit", security_audit)
builder.add_node("execute", execute_action)
builder.add_node("modify", modify_action)
builder.add_node("reject", reject_action)

builder.add_edge(START, "audit")
builder.add_conditional_edges("audit", route_approval, {
    "execute": "execute",
    "modify": "modify",
    "reject": "reject"
})
builder.add_edge("execute", END)
builder.add_edge("modify", END)
builder.add_edge("reject", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["execute", "modify", "reject"])

if __name__ == "__main__":
    print("--- Extra HITL Override Graph ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    thread = {"configurable": {"thread_id": "override-thread"}}
    initial_state = {"command": "Set temperature to 45°C", "target_device": "boiler", "auth_decision": "", "modified_params": "", "status": "Pending"}
    
    # 1. Trigger audit
    graph.invoke(initial_state, thread)
    print("Paused Node:", graph.get_state(thread).next)

    # 2. Simulate human override to "Modified" safety cap
    print("\n--- Human overrides action to MODIFIED (safety cap at 28°C) ---")
    graph.update_state(thread, {
        "auth_decision": "Modified",
        "modified_params": "Set temperature to 28°C (Max safety limit)"
    })
    graph.invoke(None, thread)
    print("Final Status:", graph.get_state(thread).values["status"])
