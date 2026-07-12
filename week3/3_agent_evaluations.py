import sys
import os
from typing import List, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class EvalState(TypedDict):
    input: str
    target_temp: int
    output_temp: int
    eval_score: float

def mock_device_runner(state: EvalState):
    # Simulate agent adjusting temperature
    input_text = state["input"].lower()
    if "24" in input_text:
        return {"output_temp": 24}
    return {"output_temp": 20}

def evaluate_temperature_accuracy(state: EvalState):
    # Evaluator compares output temp with dataset target reference temp
    score = 1.0 if state["output_temp"] == state["target_temp"] else 0.0
    return {"eval_score": score}

builder = StateGraph(EvalState)
builder.add_node("run_agent", mock_device_runner)
builder.add_node("evaluate", evaluate_temperature_accuracy)

builder.add_edge(START, "run_agent")
builder.add_edge("run_agent", "evaluate")
builder.add_edge("evaluate", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- LangGraph Agent Evaluations ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    # Simple evaluation run
    dataset = [
        {"input": "Set the room temp to 24", "target_temp": 24},
        {"input": "Set the room temp to 22", "target_temp": 22}
    ]
    
    print("\n--- Running Evaluation Dataset ---")
    for idx, test_case in enumerate(dataset, 1):
        res = graph.invoke({
            "input": test_case["input"],
            "target_temp": test_case["target_temp"],
            "output_temp": 0,
            "eval_score": 0.0
        })
        print(f"Case {idx}: Input='{res['input']}', Target={res['target_temp']}°C, Got={res['output_temp']}°C, Score={res['eval_score']}")
