import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import importlib
langgraph_101 = importlib.import_module("week2.6_langgraph_101")
graph = langgraph_101.graph

load_dotenv()

app = FastAPI(title="Ambient Smart Home Agent API")

class CommandRequest(BaseModel):
    command: str

@app.post("/invoke")
def invoke_agent(req: CommandRequest):
    """HTTP Endpoint exposing the compiled LangGraph execution graph."""
    initial_state = {
        "command": req.command,
        "target_device": "",
        "action_taken": ""
    }
    result = graph.invoke(initial_state)
    return {
        "device": result["target_device"],
        "action": result["action_taken"]
    }

if __name__ == "__main__":
    import uvicorn
    print("--- Starting FastAPI LangGraph Service ---")
    uvicorn.run(app, host="127.0.0.1", port=8000)
