import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pyrefly: ignore [missing-import]
from week2langgraph_101_extra import graph

load_dotenv()

app = FastAPI(title="Extra Ambient Smart Home Agent API with Emergency Checks")

class CommandRequest(BaseModel):
    command: str

@app.post("/invoke_extra")
def invoke_agent(req: CommandRequest):
    initial_state = {
        "command": req.command,
        "target_device": "",
        "action_taken": "",
        "is_emergency": False
    }
    result = graph.invoke(initial_state)
    return {
        "emergency": result["is_emergency"],
        "device": result["target_device"],
        "action": result["action_taken"]
    }

if __name__ == "__main__":
    import uvicorn
    print("--- Starting FastAPI Extra Service ---")
    uvicorn.run(app, host="127.0.0.1", port=8000)
