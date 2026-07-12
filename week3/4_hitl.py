import sys
import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

class HitlState(TypedDict):
    command: str
    target_device: str
    status: str

def security_audit(state: HitlState):
    # This node executes before authorization. It prompts the console.
    print(f"\n[Security Audit Log]: Request received: '{state['command']}' for device '{state['target_device']}'")
    return {"status": "Awaiting Approval"}

def execute_action(state: HitlState):
    return {"status": f"Action Approved and Executed: {state['command']}"}

# Compile Graph
builder = StateGraph(HitlState)
builder.add_node("audit", security_audit)
builder.add_node("execute", execute_action)

builder.add_edge(START, "audit")
builder.add_edge("audit", "execute")
builder.add_edge("execute", END)

# Set up memory checkpoint and interrupt
memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["execute"])

if __name__ == "__main__":
    print("--- LangGraph Human-in-the-Loop Audit ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    thread = {"configurable": {"thread_id": "hitl-thread"}}
    initial_state = {"command": "Unlock front door", "target_device": "front_door_lock", "status": "Initiated"}
    
    # Run step 1: will pause before execute
    graph.invoke(initial_state, thread)
    print("Graph execution interrupted. Status:", graph.get_state(thread).values["status"])
    
    # Resume step 2: human triggers run
    print("\n--- Human Approves Action: Resuming Graph ---")
    graph.invoke(None, thread)
    print("Final State Status:", graph.get_state(thread).values["status"])
