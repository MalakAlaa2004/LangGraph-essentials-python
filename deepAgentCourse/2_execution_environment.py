import sys
import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class SandboxState(TypedDict):
    code_to_run: str
    execution_result: str
    validation_status: str

# Simulated LocalShell execution environment sandbox
class SimulatedLocalShell:
    def execute_python_code(self, code: str) -> str:
        # Securely mock execution output of python shell sandbox
        if "print" in code:
            # Simple expression evaluation for testing
            if "50000 * 0.85" in code:
                return "42500.0"
            return "Execution successful."
        return "Error: Syntax Error"

shell = SimulatedLocalShell()

def code_writer(state: SandboxState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""Write a Python line to calculate a 15% discount on $50,000.
Use a print statement to display only the final floating value."""
    res = llm.invoke(prompt)
    # Strip markup fences if any
    code = res.content.replace("```python", "").replace("```", "").strip()
    return {"code_to_run": code}

def run_in_shell_sandbox(state: SandboxState):
    output = shell.execute_python_code(state["code_to_run"])
    return {"execution_result": output}

def validate_results(state: SandboxState):
    if state["execution_result"] == "42500.0":
        status = "PASSED: Calculation output matches expected $42,500.0 value."
    else:
        status = "FAILED: Output mismatch."
    return {"validation_status": status}

# Compile Graph
builder = StateGraph(SandboxState)
builder.add_node("writer", code_writer)
builder.add_node("sandbox_shell", run_in_shell_sandbox)
builder.add_node("validator", validate_results)

builder.add_edge(START, "writer")
builder.add_edge("writer", "sandbox_shell")
builder.add_edge("sandbox_shell", "validator")
builder.add_edge("validator", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- Module 2: Sandboxed Python Execution ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    res = graph.invoke({"code_to_run": "", "execution_result": "", "validation_status": ""})
    print("\nAgent Generated Code:", res["code_to_run"])
    # Should evaluate print(50000 * 0.85) to 42500.0
    print("Sandbox Shell Output:", res["execution_result"])
    print("Validation Check:", res["validation_status"])
