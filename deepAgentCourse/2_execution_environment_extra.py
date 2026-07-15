import sys
import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class FilesystemState(TypedDict):
    action: str # 'write' or 'read'
    file_path: str
    file_content: str
    sandbox_logs: List[str]

# Simulated Sandboxed Filesystem Backend
class SandboxFilesystem:
    def __init__(self):
        self.storage = {}
        
    def write_file(self, path: str, content: str) -> str:
        self.storage[path] = content
        return f"Successfully wrote {len(content)} bytes to /sandbox/{path}"
        
    def read_file(self, path: str) -> str:
        return self.storage.get(path, "Error: File not found.")

fs = SandboxFilesystem()

def filesystem_executor(state: FilesystemState):
    if state["action"] == "write":
        log = fs.write_file(state["file_path"], state["file_content"])
    else:
        content = fs.read_file(state["file_path"])
        log = f"Read Content: {content}"
    return {"sandbox_logs": state["sandbox_logs"] + [log]}

builder = StateGraph(FilesystemState)
builder.add_node("filesystem", filesystem_executor)
builder.add_edge(START, "filesystem")
builder.add_edge("filesystem", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- Module 2 Extra: Sandboxed Filesystem Backend ---")
    
    # 1. Write Quote file to sandbox
    print("\n--- Writing Quote file ---")
    state1 = {
        "action": "write",
        "file_path": "quotes/quote_L01.csv",
        "file_content": "ItemID,Description,Qty,Total\nSuite-01,Enterprise Cloud Suite,1,42500.0",
        "sandbox_logs": []
    }
    res1 = graph.invoke(state1)
    print("Sandbox Log:", res1["sandbox_logs"][-1])
    
    # 2. Read back from sandbox
    print("\n--- Reading back file ---")
    state2 = {
        "action": "read",
        "file_path": "quotes/quote_L01.csv",
        "file_content": "",
        "sandbox_logs": res1["sandbox_logs"]
    }
    res2 = graph.invoke(state2)
    print("Sandbox Log:", res2["sandbox_logs"][-1])
