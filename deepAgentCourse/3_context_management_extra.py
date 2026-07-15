import sys
import os
import json
from typing import TypedDict, List, Dict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

class CustomSkillsState(TypedDict):
    input: str
    loaded_skills: List[str]
    executed_skill_logs: List[str]
    response: str

# Reusable Agentic Skill Registry
class SkillRegistry:
    def __init__(self):
        self.skills = {}
        
    def register_skill(self, name: str, code_func):
        self.skills[name] = code_func
        
    def run_skill(self, name: str, state: dict) -> str:
        if name in self.skills:
            return self.skills[name](state)
        return "Skill not found."

# Skills definition
def update_crm_pipeline_skill(state: dict) -> str:
    return "CRM Updated: Stark Industries opportunity moved to 'Negotiation' stage."

registry = SkillRegistry()
registry.register_skill("update_crm", update_crm_pipeline_skill)

def load_skills_node(state: CustomSkillsState):
    # Dynamically loader selects required skills
    return {"loaded_skills": ["update_crm"]}

def execute_skills_node(state: CustomSkillsState):
    logs = []
    for skill in state["loaded_skills"]:
        log = registry.run_skill(skill, state)
        logs.append(log)
    return {"executed_skill_logs": logs}

def chat_node(state: CustomSkillsState):
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    prompt = f"""User command: {state['input']}
Executed Skills Logs: {state['executed_skill_logs']}
Summarize and confirm the action to the user."""
    res = llm.invoke(prompt)
    return {"response": res.content}

# Compile Graph
builder = StateGraph(CustomSkillsState)
builder.add_node("load_skills", load_skills_node)
builder.add_node("execute_skills", execute_skills_node)
builder.add_node("chat", chat_node)

builder.add_edge(START, "load_skills")
builder.add_edge("load_skills", "execute_skills")
builder.add_edge("execute_skills", "chat")
builder.add_edge("chat", END)

graph = builder.compile()

if __name__ == "__main__":
    print("--- Module 3 Extra: Dynamic Skills Loader ---")
    initial_state = {
        "input": "Close Stark Industries deal and update CRM.",
        "loaded_skills": [],
        "executed_skill_logs": [],
        "response": ""
    }
    res = graph.invoke(initial_state)
    print("\nLoaded Skills:", res["loaded_skills"])
    print("Executed Logs:", res["executed_skill_logs"])
    print("Response:", res["response"])
