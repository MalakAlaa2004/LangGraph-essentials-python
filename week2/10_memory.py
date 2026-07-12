import sys
import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

# Short-term memory uses LangGraph's Thread Checkpoint state
class MemoryState(TypedDict):
    input: str
    response: str

def chat_node(state: MemoryState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"User says: {state['input']}\nRespond as a helpful home assistant."
    res = llm.invoke(prompt)
    return {"response": res.content}

builder = StateGraph(MemoryState)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    print("--- LangGraph Short-Term Session Memory ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    thread = {"configurable": {"thread_id": "chat-session-45"}}
    
    # Turn 1
    print("\nTurn 1:")
    res1 = graph.invoke({"input": "Hello! I am John.", "response": ""}, thread)
    print("Assistant:", res1["response"])
    
    # Turn 2
    print("\nTurn 2 (Session checkpointer remembers state history):")
    res2 = graph.invoke({"input": "What is my name?", "response": ""}, thread)
    # The checkpointer will load the state history of John
    print("Assistant:", res2["response"])
