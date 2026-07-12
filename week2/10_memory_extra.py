import sys
import os
import json
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class UserProfileState(TypedDict):
    input: str
    user_id: str
    stored_preferences: str
    new_preference_extracted: str
    response: str

# Mock Persistent Database File
db_file = "week3/long_term_memory_db.json"

def load_profile(user_id: str) -> dict:
    if os.path.exists(db_file):
        with open(db_file, "r") as f:
            return json.load(f).get(user_id, {})
    return {}

def save_profile(user_id: str, profile: dict):
    data = {}
    if os.path.exists(db_file):
        with open(db_file, "r") as f:
            data = json.load(f)
    data[user_id] = profile
    with open(db_file, "w") as f:
        json.dump(data, f, indent=2)

# Nodes
def read_long_term_profile(state: UserProfileState):
    profile = load_profile(state["user_id"])
    return {"stored_preferences": json.dumps(profile)}

def extract_preferences(state: UserProfileState):
    """Extra Concept: Long-Term Memory Preference Extraction."""
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""User message: '{state['input']}'
Determine if the user is stating a persistent preference (e.g., 'I prefer 22 degrees in the evening', 'I hate cold showers').
If yes, return JSON format: {{"preference_found": true, "key": "temperature", "value": "22C"}}.
If no, return {{"preference_found": false}}."""
    res = llm.invoke(prompt)
    try:
        data = json.loads(res.content)
        if data.get("preference_found"):
            # Update database
            profile = load_profile(state["user_id"])
            profile[data["key"]] = data["value"]
            save_profile(state["user_id"], profile)
            return {"new_preference_extracted": f"Saved preference: {data['key']} = {data['value']}"}
    except:
        pass
    return {"new_preference_extracted": "None"}

def chat_node(state: UserProfileState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""User input: {state['input']}
User Stored Profile: {state['stored_preferences']}
Respond as a smart home assistant, acknowledging their preferences if relevant."""
    res = llm.invoke(prompt)
    return {"response": res.content}

# Compile Graph
builder = StateGraph(UserProfileState)
builder.add_node("load_profile", read_long_term_profile)
builder.add_node("extract", extract_preferences)
builder.add_node("chat", chat_node)

builder.add_edge(START, "load_profile")
builder.add_edge("load_profile", "extract")
builder.add_edge("extract", "chat")
builder.add_edge("chat", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    print("--- Extra Long-Term Memory Syncer ---")
    try:
        print(graph.get_graph().draw_ascii())
    except:
        pass

    # Clear previous run DB
    if os.path.exists(db_file):
        os.remove(db_file)

    thread = {"configurable": {"thread_id": "user-session-12"}}
    state_args = {
        "input": "From now on, I prefer my living room temperature at 23 degrees in the evening.",
        "user_id": "user_john_doe",
        "stored_preferences": "",
        "new_preference_extracted": "",
        "response": ""
    }
    
    # Run 1: Preference is stated and saved in DB
    print("\n--- Run 1: User states long-term preference ---")
    res1 = graph.invoke(state_args, thread)
    print("Extracted Info:", res1["new_preference_extracted"])
    print("Assistant:", res1["response"])
    
    # Run 2: New session (different thread_id), but same user_id
    print("\n--- Run 2: New Session. Assistant recalls preference from Database ---")
    thread2 = {"configurable": {"thread_id": "user-session-99"}}
    state_args2 = {
        "input": "Turn on the heat in the living room.",
        "user_id": "user_john_doe",
        "stored_preferences": "",
        "new_preference_extracted": "",
        "response": ""
    }
    res2 = graph.invoke(state_args2, thread2)
    print("Retrieved profile data from DB:", res2["stored_preferences"])
    print("Assistant:", res2["response"])
