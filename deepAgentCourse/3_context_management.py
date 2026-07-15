import sys
import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class ContextState(TypedDict):
    chat_history: List[str]
    summary: str
    incoming_query: str
    response: str

def summarize_history(state: ContextState):
    """Summarizes long history to manage context window limits."""
    history_len = len(state["chat_history"])
    # If history is long (simulated here as > 2 messages), compress it
    if history_len > 2:
        llm = get_llm(model="gpt-4o-mini", temperature=0)
        history_str = "\n".join(state["chat_history"])
        prompt = f"Summarize this sales conversation history concisely:\n{history_str}"
        res = llm.invoke(prompt)
        # Clear out chat history list and save summary
        return {
            "summary": res.content,
            "chat_history": [] # Offloaded history
        }
    return {}

def chat_node(state: ContextState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    context = f"Summary of past conversation: {state['summary']}\n" if state["summary"] else ""
    history = "\n".join(state["chat_history"]) + "\n" if state["chat_history"] else ""
    
    prompt = f"""Context: {context}{history}
Customer Query: {state['incoming_query']}
Respond as the Tech Sales Assistant."""
    res = llm.invoke(prompt)
    return {
        "response": res.content,
        "chat_history": state["chat_history"] + [f"User: {state['incoming_query']}", f"Assistant: {res.content}"]
    }

builder = StateGraph(ContextState)
builder.add_node("summarizer", summarize_history)
builder.add_node("chat", chat_node)

builder.add_edge(START, "summarizer")
builder.add_edge("summarizer", "chat")
builder.add_edge("chat", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- Module 3: Context Summarization & Offloading ---")
    
    # Start with long history
    initial_state = {
        "chat_history": [
            "User: Hi, what is the price of the Cloud Suite?",
            "Assistant: It is $50,000 per year.",
            "User: Do you offer bulk discounts?",
            "Assistant: Yes, for more than 10 units we offer a 15% discount."
        ],
        "summary": "",
        "incoming_query": "Great, we want to buy 12 units.",
        "response": ""
    }
    
    res = graph.invoke(initial_state)
    print("\nGenerated Summary (Offloaded History):", res["summary"])
    print("New Active History Queue:", res["chat_history"][-2:])
    print("Assistant Response:", res["response"])
