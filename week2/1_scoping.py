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

class ScopingState(TypedDict):
    topic: str
    questions: List[str]
    answers: List[str]
    brief: str

def generate_clarification_questions(state: ScopingState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Analyze this research topic: '{state['topic']}'
Formulate exactly 3 clarifying questions to narrow down the scope (focus area, depth, target audience).
Return JSON format: {{"questions": ["Q1", "Q2", "Q3"]}}"""
    res = llm.invoke(prompt)
    try:
        data = json.loads(res.content)
        questions = data["questions"]
    except:
        questions = [
            "Which specific financial systems (e.g. SWIFT, local banks) are we prioritizing for PQC migration?",
            "Should we focus primarily on lattice-based key encapsulation mechanisms (ML-KEM)?",
            "What is the target timeline for the migration roadmap (e.g. 3-year vs 10-year outlook)?"
        ]
    return {"questions": questions}

def generate_brief(state: ScopingState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    qa_pairs = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(state["questions"], state["answers"])])
    prompt = f"""Compile a structured Research Brief for topic: {state['topic']}
Q&A Context:
{qa_pairs}

Format the output clearly in markdown with sections for: Topic, Technical Focus, Scope Constraints, and Execution Roadmap."""
    res = llm.invoke(prompt)
    return {"brief": res.content}

# Compile Graph
builder = StateGraph(ScopingState)
builder.add_node("ask_questions", generate_clarification_questions)
builder.add_node("generate_brief", generate_brief)
builder.add_edge(START, "ask_questions")
builder.add_edge("ask_questions", "generate_brief")
builder.add_edge("generate_brief", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["generate_brief"])

if __name__ == "__main__":
    print("--- LangGraph Scoping Architecture ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    thread = {"configurable": {"thread_id": "scope-thread"}}
    
    # Run step 1
    print("\n--- Starting Scoping Node ---")
    initial_state = {"topic": "Post-Quantum Cryptography Migration for Financial Systems", "answers": []}
    for event in graph.stream(initial_state, thread, stream_mode="values"):
        if event.get("questions"):
            print("\nClarifying Questions:")
            for idx, q in enumerate(event["questions"], 1):
                print(f" {idx}. {q}")
                
    # Resume step 2 (answers)
    answers = [
        "Primary focus is core transaction gateways like SWIFT and interbank settlement systems.",
        "Yes, prioritize FIPS 203 standards (specifically ML-KEM and ML-DSA).",
        "Targeting a realistic 5-year migration roadmap (2026-2031)."
    ]
    print("\n--- Injecting Answers & Resuming Graph ---")
    graph.update_state(thread, {"answers": answers})
    res = graph.invoke(None, thread)
    print("\nFinal Research Brief:\n")
    print(res["brief"])
