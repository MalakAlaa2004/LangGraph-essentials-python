import sys
import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class AmbientState(TypedDict):
    command: str
    target_device: str
    action_taken: str
    is_emergency: bool

def parser_node(state: AmbientState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Analyze command: '{state['command']}'
Determine if it is a security emergency. Return JSON: {{"emergency": true/false, "device": "device_name"}}"""
    # Simple check for demo
    cmd = state["command"].lower()
    emergency = "fire" in cmd or "smoke" in cmd or "intruder" in cmd
    device = "alarm" if emergency else "thermostat"
    if "light" in cmd: device = "lights"
    return {"is_emergency": emergency, "target_device": device}

def normal_executor(state: AmbientState):
    return {"action_taken": f"Standard adjustment completed on {state['target_device']}."}

def emergency_executor(state: AmbientState):
    return {"action_taken": f"ALARM TRIGGERED! Emergency protocol active for {state['target_device']}!"}

def route_urgency(state: AmbientState):
    """Extra Concept: Dynamic Expression Router. Routes state based on boolean values."""
    if state["is_emergency"]:
        return "emergency_node"
    return "normal_node"

# Compile Graph
builder = StateGraph(AmbientState)
builder.add_node("parser", parser_node)
builder.add_node("normal_node", normal_executor)
builder.add_node("emergency_node", emergency_executor)

builder.add_edge(START, "parser")
builder.add_conditional_edges("parser", route_urgency, {
    "normal_node": "normal_node",
    "emergency_node": "emergency_node"
})
builder.add_edge("normal_node", END)
builder.add_edge("emergency_node", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- Extra 101 Graph with Emergency Branching ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    print("\n--- Test 1: Normal Command ---")
    res1 = graph.invoke({"command": "Set thermostat to 22 degrees", "target_device": "", "action_taken": "", "is_emergency": False})
    print("Action Result:", res1["action_taken"])

    print("\n--- Test 2: Emergency Command ---")
    res2 = graph.invoke({"command": "Intruder detected in back garden!", "target_device": "", "action_taken": "", "is_emergency": False})
    print("Action Result:", res2["action_taken"])
