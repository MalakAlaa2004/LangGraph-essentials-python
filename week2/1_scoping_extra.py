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
    validation_feedback: str
    brief: str

def generate_clarification_questions(state: ScopingState):
    return {"questions": [
        "Which specific transaction gateways (e.g. SWIFT, FedWire) are in scope?",
        "Should we prioritize NIST's FIPS 203 lattice standards?",
        "What is the target transition window?"
    ]}

def validate_answers(state: ScopingState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Evaluate the user's answers to the clarifying questions.
Questions: {state['questions']}
Answers: {state['answers']}

Are these answers descriptive enough to compile a brief? If they are too short or vague, return a review critique.
Return JSON format: {{"valid": true/false, "feedback": "Critique if invalid, otherwise empty"}}"""
    res = llm.invoke(prompt)
    try:
        data = json.loads(res.content)
        valid = data["valid"]
        feedback = data["feedback"]
    except:
        vague = any(len(a.strip()) < 10 for a in state["answers"])
        valid = not vague
        feedback = "Please provide more details for each question." if vague else ""
    
    return {"validation_feedback": feedback}

def route_validation(state: ScopingState):
    if state.get("validation_feedback"):
        print(f"\n[Validation Failed]: {state['validation_feedback']}")
        return "ask_questions"
    return "generate_brief"

def generate_brief(state: ScopingState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Compile a Research Brief for topic: {state['topic']}
Answers: {state['answers']}"""
    res = llm.invoke(prompt)
    return {"brief": res.content}

# Compile Graph
builder = StateGraph(ScopingState)
builder.add_node("ask_questions", generate_clarification_questions)
builder.add_node("validate", validate_answers)
builder.add_node("generate_brief", generate_brief)

builder.add_edge(START, "ask_questions")
builder.add_edge("ask_questions", "validate")
builder.add_conditional_edges("validate", route_validation, {
    "ask_questions": "ask_questions",
    "generate_brief": "generate_brief"
})
builder.add_edge("generate_brief", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["validate"])

if __name__ == "__main__":
    print("--- Extra Scoping Graph with Input Validation Loop ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    thread = {"configurable": {"thread_id": "scope-extra-thread"}}
    
    # 1. Ask questions
    graph.invoke({"topic": "PQC Migration", "answers": [], "validation_feedback": "", "brief": ""}, thread)
    print("\nQuestions asked. State paused.")

    # 2. Provide vague answers first (Validation Loop test)
    print("\n--- Test 1: Simulating vague answers (Should trigger loop back) ---")
    graph.update_state(thread, {"answers": ["SWIFT", "Yes", "Now"]})
    res = graph.invoke(None, thread)
    
    # 3. Provide descriptive answers (Validation Pass test)
    print("\n--- Test 2: Simulating descriptive answers (Should pass) ---")
    graph.update_state(thread, {
        "answers": [
            "We are focusing on SWIFT payment channels and local central bank interfaces.",
            "Yes, we must align specifically with NIST FIPS 203 lattice algorithms (ML-KEM).",
            "Our migration target timeline is set to be completed within 5 years."
        ],
        "validation_feedback": ""
    })
    res = graph.invoke(None, thread)
    print("\nFinal Brief Result:")
    print(res["brief"])
