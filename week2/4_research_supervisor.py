import sys
import os
import json
from typing import List, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class SupervisorState(TypedDict):
    brief: str
    notes: str
    next_agent: str
    report: str

def supervisor(state: SupervisorState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""State of notes: {state['notes']}
Select next analyst to run: 'market_analyst', 'technical_analyst', or 'compile_report'.
Return JSON: {{"next_agent": "name"}}"""
    res = llm.invoke(prompt)
    try:
        data = json.loads(res.content)
        next_agent = data["next_agent"]
    except:
        if "market" not in state["notes"].lower():
            next_agent = "market_analyst"
        elif "technical" not in state["notes"].lower():
            next_agent = "technical_analyst"
        else:
            next_agent = "compile_report"
    return {"next_agent": next_agent}

def market_analyst(state: SupervisorState):
    new_notes = state["notes"] + "\n[Market Analyst] PQC financial migration roadmap is budgeted at $2.4B globally."
    return {"notes": new_notes}

def technical_analyst(state: SupervisorState):
    new_notes = state["notes"] + "\n[Technical Analyst] FIPS 203 lattice-based ML-KEM-768 is selected as primary key agreement algorithm."
    return {"notes": new_notes}

def report_compiler(state: SupervisorState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Compile a final report from notes: {state['notes']}"""
    res = llm.invoke(prompt)
    return {"report": res.content}

def route_next(state: SupervisorState):
    return state["next_agent"]

# Compile Graph
builder = StateGraph(SupervisorState)
builder.add_node("supervisor", supervisor)
builder.add_node("market_analyst", market_analyst)
builder.add_node("technical_analyst", technical_analyst)
builder.add_node("compile_report", report_compiler)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route_next, {
    "market_analyst": "market_analyst",
    "technical_analyst": "technical_analyst",
    "compile_report": "compile_report"
})
builder.add_edge("market_analyst", "supervisor")
builder.add_edge("technical_analyst", "supervisor")
builder.add_edge("compile_report", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- LangGraph Research Supervisor Graph ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    initial_state = {
        "brief": "Perform market and tech evaluations for financial PQC migration.",
        "notes": "Initial report base.",
        "next_agent": "",
        "report": ""
    }
    
    res = graph.invoke(initial_state)
    print("\nFinal Compiled Report:")
    print(res["report"])
