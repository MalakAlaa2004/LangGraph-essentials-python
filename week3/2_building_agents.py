import sys
import os
import json
from typing import List, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class AgentState(TypedDict):
    input: str
    target_temp: int
    current_temp: int
    log: List[str]

def smart_thermostat_tool(action: str, temp: int) -> str:
    return f"Smart Thermostat updated: Action={action}, NewTemp={temp}°C"

def react_agent(state: AgentState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Command: {state['input']}
Current Room Temperature: {state['current_temp']}°C
Determine if we need to call smart_thermostat_tool.
Return JSON format: {{"tool_call": true/false, "action": "heat/cool", "temp": target_temp}}"""
    res = llm.invoke(prompt)
    try:
        data = json.loads(res.content)
        tool_call = data["tool_call"]
        action = data["action"]
        temp = data["temp"]
    except:
        tool_call = True
        action = "heat"
        temp = 22
        
    return {
        "target_temp": temp,
        "log": state["log"] + [f"Agent decision: CallTool={tool_call}, Action={action}, Temp={temp}"]
    }

def tool_executor(state: AgentState):
    action = "heat" if state["target_temp"] > state["current_temp"] else "cool"
    result = smart_thermostat_tool(action, state["target_temp"])
    return {
        "current_temp": state["target_temp"],
        "log": state["log"] + [result]
    }

builder = StateGraph(AgentState)
builder.add_node("agent", react_agent)
builder.add_node("tools", tool_executor)

builder.add_edge(START, "agent")
builder.add_edge("agent", "tools")
builder.add_edge("tools", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- ReAct Agent Smart Thermostat ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    initial_state = {
        "input": "Make the room warmer. Set to 24 degrees.",
        "target_temp": 0,
        "current_temp": 19,
        "log": []
    }
    res = graph.invoke(initial_state)
    print("\nExecution Logs:")
    for log in res["log"]:
        print(f" - {log}")
