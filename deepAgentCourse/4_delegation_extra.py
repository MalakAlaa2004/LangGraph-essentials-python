import sys
import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

# Parent Agent State
class ParentState(TypedDict):
    user_query: str
    delegated_task: str
    child_output: str
    final_response: str

# Child Agent State
class ChildState(TypedDict):
    task: str
    child_logs: List[str]
    result: str

# Define Child Graph
def child_worker_node(state: ChildState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    res = llm.invoke(f"Execute task: {state['task']}")
    return {
        "result": res.content,
        "child_logs": state["child_logs"] + [f"Child worked on: {state['task']}"]
    }

child_builder = StateGraph(ChildState)
child_builder.add_node("worker", child_worker_node)
child_builder.add_edge(START, "worker")
child_builder.add_edge("worker", END)
child_graph = child_builder.compile()

# Parent Nodes
def delegate_to_child(state: ParentState):
    # Prepares data and runs child graph
    print("\n[Parent Node]: Delegating context to child graph...")
    child_initial_state = {
        "task": state["user_query"],
        "child_logs": [],
        "result": ""
    }
    child_res = child_graph.invoke(child_initial_state)
    return {"child_output": child_res["result"]}

def parent_synthesizer(state: ParentState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Parent query: {state['user_query']}
Child generated answer: {state['child_output']}
Compile the final response."""
    res = llm.invoke(prompt)
    return {"final_response": res.content}

# Compile Parent Graph
builder = StateGraph(ParentState)
builder.add_node("delegate", delegate_to_child)
builder.add_node("synthesize", parent_synthesizer)

builder.add_edge(START, "delegate")
builder.add_edge("delegate", "synthesize")
builder.add_edge("synthesize", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- Module 4 Extra: Parent-Child Context Delegation ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    initial_state = {
        "user_query": "Draft a contract template for Stark Industries.",
        "delegated_task": "",
        "child_output": "",
        "final_response": ""
    }
    res = graph.invoke(initial_state)
    print("Final Parent Output:", res["final_response"])
