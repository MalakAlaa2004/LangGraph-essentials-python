import sys
import os
import json
from typing import List, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class FullSystemState(TypedDict):
    topic: str
    questions: List[str]
    answers: List[str]
    brief: str
    notes: str
    next_agent: str
    report: str

def scoping_ask(state: FullSystemState):
    return {"questions": [
        "Which specific transaction gateways (e.g. SWIFT, FedWire) are in scope?",
        "Should we prioritize NIST's FIPS 203 lattice standards?",
        "What is the target transition window?"
    ]}

def scoping_brief(state: FullSystemState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Draft a research brief for {state['topic']} based on answers: {state['answers']}"""
    res = llm.invoke(prompt)
    return {"brief": res.content, "notes": "Initial Briefing details set."}

def supervisor(state: FullSystemState):
    if "market" not in state["notes"].lower():
        next_agent = "market_analyst"
    elif "technical" not in state["notes"].lower():
        next_agent = "technical_analyst"
    else:
        next_agent = "compile_report"
    return {"next_agent": next_agent}

def market_analyst(state: FullSystemState):
    new_notes = state["notes"] + "\n[Market Findings] Financial systems PQC upgrades total $2.4B globally."
    return {"notes": new_notes}

def technical_analyst(state: FullSystemState):
    new_notes = state["notes"] + "\n[Technical Findings] NIST finalized standards for ML-KEM-768."
    return {"notes": new_notes}

def report_compiler(state: FullSystemState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Compile final report from notes: {state['notes']}"""
    res = llm.invoke(prompt)
    return {"report": res.content}

def route_next(state: FullSystemState):
    return state["next_agent"]

# Compile Graph
builder = StateGraph(FullSystemState)
builder.add_node("scoping_ask", scoping_ask)
builder.add_node("scoping_brief", scoping_brief)
builder.add_node("supervisor", supervisor)
builder.add_node("market_analyst", market_analyst)
builder.add_node("technical_analyst", technical_analyst)
builder.add_node("compile_report", report_compiler)

builder.add_edge(START, "scoping_ask")
builder.add_edge("scoping_ask", "scoping_brief")
builder.add_edge("scoping_brief", "supervisor")

builder.add_conditional_edges("supervisor", route_next, {
    "market_analyst": "market_analyst",
    "technical_analyst": "technical_analyst",
    "compile_report": "compile_report"
})
builder.add_edge("market_analyst", "supervisor")
builder.add_edge("technical_analyst", "supervisor")
builder.add_edge("compile_report", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["scoping_brief"])

if __name__ == "__main__":
    print("--- Full Multi-Agent Research System ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    thread = {"configurable": {"thread_id": "full-thread"}}
    
    # Start Scoping
    graph.invoke({"topic": "PQC Migration", "answers": [], "brief": "", "notes": "", "next_agent": "", "report": ""}, thread)
    print("\nPaused after questions. Updating answers...")

    # Resume with answers
    graph.update_state(thread, {"answers": [
        "SWIFT interbank gateways.",
        "Yes, NIST FIPS 203 (ML-KEM-768).",
        "Completed within 5 years."
    ]})
    
    res = graph.invoke(None, thread)
    print("\nFinal Multi-Agent Compiled Report:")
    print(res["report"])
