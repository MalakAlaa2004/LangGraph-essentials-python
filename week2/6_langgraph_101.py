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

def command_parser(state: AmbientState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Classify the target device for this command: '{state['command']}'
Return only the device name (e.g. thermostat, lights, lock)."""
    res = llm.invoke(prompt)
    return {"target_device": res.content.strip().lower()}

def action_executor(state: AmbientState):
    device = state["target_device"]
    command = state["command"]
    action = f"Executed: {command} on device {device}"
    return {"action_taken": action}

# Compile Graph
builder = StateGraph(AmbientState)
builder.add_node("parser", command_parser)
builder.add_node("executor", action_executor)

builder.add_edge(START, "parser")
builder.add_edge("parser", "executor")
builder.add_edge("executor", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- LangGraph 101 Smart Home Ambient Agent ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    initial_state = {"command": "Turn off the kitchen lights", "target_device": "", "action_taken": ""}
    res = graph.invoke(initial_state)
    print(f"\nParsed Target Device: {res['target_device']}")
    print(f"Action Output: {res['action_taken']}")
