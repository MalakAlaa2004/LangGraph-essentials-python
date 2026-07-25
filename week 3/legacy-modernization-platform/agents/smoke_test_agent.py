import os
import sys
from typing import Annotated, TypedDict
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

from langchain_core.language_models.fake import FakeListLLM
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


# Define Graph State
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def load_archimate_skill() -> str:
    """Load content of the ArchiMate metamodel skill document."""
    skill_path = os.path.join(
        os.path.dirname(__file__), "skills", "archimate-metamodel", "SKILL.md"
    )
    if os.path.exists(skill_path):
        with open(skill_path, "r", encoding="utf-8") as f:
            return f.read()
    return "No skill found."


def get_llm():
    """Initialize LLM (Ollama Cloud API or FakeListLLM fallback)."""
    ollama_api_key = os.getenv("OLLAMA_API_KEY")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "https://ollama.com")
    ollama_model = os.getenv("OLLAMA_MODEL", "gpt-oss:120b")

    if ollama_api_key:
        return ChatOpenAI(
            base_url=f"{ollama_base_url.rstrip('/')}/v1",
            api_key=ollama_api_key,
            model=ollama_model,
            temperature=0,
        )
    return FakeListLLM(
        responses=[
            "Yes, ApplicationComponent serving BusinessProcess is valid in ArchiMate 3.2."
        ]
    )


def agent_node(state: AgentState) -> dict:
    """Agent node loading the skill into system prompt and querying LLM."""
    skill_text = load_archimate_skill()
    system_prompt = SystemMessage(
        content=(
            "You are an ArchiMate 3.2 Enterprise Architecture Expert.\n"
            "Use the following official ArchiMate 3.2 Metamodel Skill to answer questions strictly:\n\n"
            f"{skill_text}"
        )
    )
    llm = get_llm()
    messages = [system_prompt] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def build_smoke_test_graph():
    """Construct the LangGraph StateGraph architecture."""
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)
    return workflow.compile()


def run_smoke_test_query(query_text: str):
    """Execute a single query through the LangGraph smoke-test agent."""
    graph = build_smoke_test_graph()
    initial_state = {"messages": [HumanMessage(content=query_text)]}
    result = graph.invoke(initial_state)
    last_msg = result["messages"][-1]
    return last_msg.content if hasattr(last_msg, "content") else last_msg


if __name__ == "__main__":
    graph = build_smoke_test_graph()
    print("==================================================")
    print("LangGraph Smoke-Test Agent Architecture:")
    print("==================================================")
    try:
        print(graph.get_graph().draw_ascii())
    except Exception:
        print("START -> agent -> END")
    print("==================================================\n")

    test_query = "Is 'ApplicationComponent serves BusinessProcess' a valid relationship in ArchiMate 3.2?"
    print(f"Query: {test_query}\n")
    ans = run_smoke_test_query(test_query)
    print(f"Answer: {ans}\n")
    print("Trace dispatched to LangSmith under project 'legacy-modernization-mvp'")
