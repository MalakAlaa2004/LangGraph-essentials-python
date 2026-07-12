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

class SupervisorState(TypedDict):
    brief: str
    findings: Annotated[List[str], operator.add]
    report: str

def market_analyst(state: SupervisorState):
    return {"findings": ["[Market Analyst] Corporate spending on PQC transition software is estimated at $2.4B."]}

def technical_analyst(state: SupervisorState):
    return {"findings": ["[Technical Analyst] NIST recommends ML-KEM-768 for transaction-level payload encryption."]}

def report_compiler(state: SupervisorState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Compile these separate research papers: {state['findings']}
Into a unified, detailed financial research brief."""
    res = llm.invoke(prompt)
    return {"report": res.content}

# Compile Graph
builder = StateGraph(SupervisorState)
builder.add_node("market_analyst", market_analyst)
builder.add_node("technical_analyst", technical_analyst)
builder.add_node("compile_report", report_compiler)

# Parallel Branching (Fork-Join)
builder.add_edge(START, "market_analyst")
builder.add_edge(START, "technical_analyst")
builder.add_edge("market_analyst", "compile_report")
builder.add_edge("technical_analyst", "compile_report")
builder.add_edge("compile_report", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- Extra Supervisor Parallel Branching (Map-Reduce) ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    initial_state = {
        "brief": "Quantum readiness benchmark.",
        "findings": [],
        "report": ""
    }
    
    res = graph.invoke(initial_state)
    print("\nAccumulated Parallel Findings:", res["findings"])
    print("\nFinal Compiled Report:")
    print(res["report"])
