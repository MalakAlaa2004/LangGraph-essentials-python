import sys
import os
import json
import operator
from typing import List, TypedDict, Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class ParallelAgentState(TypedDict):
    input: str
    target_temp: int
    sensor_logs: Annotated[List[str], operator.add]
    action_log: str

# Tools
def check_temp_sensor() -> str:
    return "Living Room Sensor: Temp=18°C"

def check_humidity_sensor() -> str:
    return "Living Room Sensor: Humidity=65%"

# Nodes
def sensor_hub(state: ParallelAgentState):
    # Triggers parallel readings
    return {}

def read_temp(state: ParallelAgentState):
    return {"sensor_logs": [check_temp_sensor()]}

def read_humidity(state: ParallelAgentState):
    return {"sensor_logs": [check_humidity_sensor()]}

def react_agent(state: ParallelAgentState):
    """Extra Concept: Multi-Sensor Aggregation. Synthesizes inputs from multiple parallel sources."""
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""User Goal: {state['input']}
Sensor Readings: {state['sensor_logs']}
Determine final action log. Return updated summary."""
    res = llm.invoke(prompt)
    return {"action_log": res.content}

# Compile Graph
builder = StateGraph(ParallelAgentState)
builder.add_node("hub", sensor_hub)
builder.add_node("read_temp", read_temp)
builder.add_node("read_humidity", read_humidity)
builder.add_node("agent", react_agent)

builder.add_edge(START, "hub")
# Parallel Fork to read sensors
builder.add_edge("hub", "read_temp")
builder.add_edge("hub", "read_humidity")
# Merge / Join to agent
builder.add_edge("read_temp", "agent")
builder.add_edge("read_humidity", "agent")
builder.add_edge("agent", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- Extra Multi-Sensor ReAct Agent (Parallel Branching) ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    initial_state = {
        "input": "Check the room climate and make it comfortable.",
        "target_temp": 22,
        "sensor_logs": [],
        "action_log": ""
    }
    res = graph.invoke(initial_state)
    print("\nAccumulated Sensor Outputs:", res["sensor_logs"])
    print("\nAgent Synthesis:", res["action_log"])
