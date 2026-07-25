import os
import sys
from typing import Annotated, Optional, TypedDict
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

from backend.services.git_storage_service import GitStorageService


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


class BaseDeepAgent:
    """Base reusable Deep Agent wrapper for multi-agent workflows."""

    def __init__(
        self,
        agent_name: str,
        skill_name: Optional[str] = None,
        base_storage_dir: Optional[str] = None,
    ):
        self.agent_name = agent_name
        self.skill_name = skill_name

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        storage_dir = base_storage_dir or os.path.join(project_root, "test-fixtures")
        self.storage_service = GitStorageService(storage_dir)

    def load_skill_content(self) -> str:
        """Load content of a specified skill file."""
        if not self.skill_name:
            return ""
        skill_path = os.path.join(
            os.path.dirname(__file__), "skills", self.skill_name, "SKILL.md"
        )
        if os.path.exists(skill_path):
            with open(skill_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def get_llm(self):
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
                f"BaseDeepAgent [{self.agent_name}] processed response successfully."
            ]
        )

    def agent_node(self, state: AgentState) -> dict:
        """Core execution node for the agent."""
        skill_text = self.load_skill_content()
        system_content = f"You are the '{self.agent_name}' subagent in the Legacy Modernization Platform."
        if skill_text:
            system_content += f"\n\nReference Skill Information:\n{skill_text}"

        system_message = SystemMessage(content=system_content)
        llm = self.get_llm()
        messages = [system_message] + state["messages"]
        response = llm.invoke(messages)
        return {"messages": [response]}

    def build_graph(self):
        """Construct and compile the LangGraph StateGraph architecture."""
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self.agent_node)
        workflow.add_edge(START, "agent")
        workflow.add_edge("agent", END)
        return workflow.compile()

    def run(self, prompt: str) -> str:
        """Run a prompt through the agent and return string response."""
        graph = self.build_graph()
        initial_state = {"messages": [HumanMessage(content=prompt)]}
        result = graph.invoke(initial_state)
        last_msg = result["messages"][-1]
        return last_msg.content if hasattr(last_msg, "content") else last_msg


if __name__ == "__main__":
    agent = BaseDeepAgent(
        agent_name="base_architecture_agent", skill_name="archimate-metamodel"
    )
    graph = agent.build_graph()
    print("==================================================")
    print(f"BaseDeepAgent [{agent.agent_name}] Graph Architecture:")
    print("==================================================")
    try:
        print(graph.get_graph().draw_ascii())
    except Exception:
        print("START -> agent -> END")
    print("==================================================\n")

    res = agent.run("Summarize the purpose of the Technology layer in ArchiMate 3.2.")
    print(f"Agent Response: {res}\n")
    print("Trace dispatched to LangSmith under project 'legacy-modernization-mvp'")
