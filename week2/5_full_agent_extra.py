import sys
import os
import json
import operator
from typing import List, TypedDict, Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class FullSystemExtraState(TypedDict):
    topic: str
    questions: List[str]
    answers: List[str]
    brief: str
    findings: Annotated[List[str], operator.add]
    report: str

def scoping_ask(state: FullSystemExtraState):
    return {"questions": [
        "Which specific transaction gateways are in scope?",
        "Should we prioritize NIST FIPS 203?",
        "What is the timeline target?"
    ]}

def scoping_brief(state: FullSystemExtraState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Draft a brief for {state['topic']} based on answers: {state['answers']}"""
    res = llm.invoke(prompt)
    return {"brief": res.content, "findings": ["[Scoping Brief]: Topic initialized."]}

def market_analyst(state: FullSystemExtraState):
    return {"findings": ["[Market Analyst] Financial systems PQC upgrades total $2.4B."]}

def technical_analyst(state: FullSystemExtraState):
    return {"findings": ["[Technical Analyst] NIST finalized standard parameters for ML-KEM-768."]}

def report_compiler(state: FullSystemExtraState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Compile final report from findings: {state['findings']}"""
    res = llm.invoke(prompt)
    return {"report": res.content}

def human_approval(state: FullSystemExtraState):
    print("\n--- Report submitted for Human-in-the-loop Review ---")
    return {}

# Compile Graph
builder = StateGraph(FullSystemExtraState)
builder.add_node("scoping_ask", scoping_ask)
builder.add_node("scoping_brief", scoping_brief)
builder.add_node("market_analyst", market_analyst)
builder.add_node("technical_analyst", technical_analyst)
builder.add_node("compile_report", report_compiler)
builder.add_node("human_review", human_approval)

builder.add_edge(START, "scoping_ask")
builder.add_edge("scoping_ask", "scoping_brief")

# Parallel branch research
builder.add_edge("scoping_brief", "market_analyst")
builder.add_edge("scoping_brief", "technical_analyst")
builder.add_edge("market_analyst", "compile_report")
builder.add_edge("technical_analyst", "compile_report")

builder.add_edge("compile_report", "human_review")
builder.add_edge("human_review", END)

memory = MemorySaver()
graph = builder.compile(
    checkpointer=memory, 
    interrupt_before=["scoping_brief", "human_review"]
)

if __name__ == "__main__":
    print("--- Extra Full System: Dual Interrupt (Scoping + Human Review) & Parallel Research ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    thread = {"configurable": {"thread_id": "full-extra-thread"}}
    
    # 1. Start Scoping
    graph.invoke({"topic": "PQC", "answers": [], "brief": "", "findings": [], "report": ""}, thread)
    
    # 2. Update answers and run (will pause at human review)
    print("\n--- Injecting Scoping Answers ---")
    graph.update_state(thread, {"answers": [
        "SWIFT gateways.",
        "Yes, FIPS 203.",
        "Completed within 5 years."
    ]})
    graph.invoke(None, thread)
    
    state = graph.get_state(thread)
    print("\nPaused Node:", state.next)
    
    # 3. Approve and Finalize
    print("\n--- Human Approves/Edits Report directly and Finalizes ---")
    graph.update_state(thread, {"report": state.values["report"] + "\n[Human Signature]: Reviewed and Approved."})
    res = graph.invoke(None, thread)
    print("\nFinal Output Report:")
    print(res["report"])
