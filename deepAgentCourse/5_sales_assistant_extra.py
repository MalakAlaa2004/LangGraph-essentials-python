import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import importlib
sales_module = importlib.import_module("deepAgentCourse.5_sales_assistant")
graph = sales_module.graph

load_dotenv()

app = FastAPI(title="B2B Tech Sales Assistant Deployed Service API")

class DealRequest(BaseModel):
    query: str

@app.post("/deal_pipeline")
def run_deal_pipeline(req: DealRequest):
    # Trigger graph execution
    initial_state = {
        "customer_query": req.query,
        "inventory_checked": False,
        "quote_calculated": 0.0,
        "manager_approved": False,
        "response": "",
        "logs": []
    }
    # For demo we run it sync bypassing interrupt
    result = graph.invoke(initial_state)
    return {
        "quote": result["quote_calculated"],
        "logs": result["logs"]
    }

if __name__ == "__main__":
    import uvicorn
    print("--- Starting FastAPI Deployed Sales Assistant Service ---")
    uvicorn.run(app, host="127.0.0.1", port=8000)
