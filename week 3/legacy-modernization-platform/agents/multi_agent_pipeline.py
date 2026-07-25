import os
import sys
from typing import Annotated, List, TypedDict
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from agents.base_agent import BaseDeepAgent


class PipelineState(TypedDict):
    system_id: str
    messages: Annotated[list[BaseMessage], add_messages]
    processed_layers: List[str]
    elements_count: int


def create_layer_node(layer_name: str):
    """Factory creating a pipeline node for a specific ArchiMate layer."""
    agent = BaseDeepAgent(
        agent_name=f"{layer_name}_agent", skill_name="archimate-metamodel"
    )

    def node_function(state: PipelineState) -> dict:
        system_id = state.get("system_id", "system-demo")
        elements = agent.storage_service.list_model_elements(
            system_id=system_id, layer=layer_name
        )

        node_msg = (
            f"[{layer_name.upper()} AGENT]: Loaded {len(elements)} elements for layer '{layer_name}' "
            f"in system '{system_id}'."
        )

        # Invoke agent for processing
        res = agent.run(
            f"Summarize processing for layer '{layer_name}' with {len(elements)} elements."
        )

        processed = state.get("processed_layers", []) + [layer_name]
        count = state.get("elements_count", 0) + len(elements)

        return {
            "messages": [HumanMessage(content=node_msg)],
            "processed_layers": processed,
            "elements_count": count,
        }

    return node_function


def build_multi_agent_pipeline():
    """Build and compile the 5-subagent LangGraph pipeline."""
    workflow = StateGraph(PipelineState)

    # Add 5 layer subagent nodes
    workflow.add_node("motivation_agent", create_layer_node("motivation"))
    workflow.add_node("strategy_agent", create_layer_node("strategy"))
    workflow.add_node("business_agent", create_layer_node("business"))
    workflow.add_node("application_agent", create_layer_node("application"))
    workflow.add_node("technology_agent", create_layer_node("technology"))

    # Connect nodes sequentially
    workflow.add_edge(START, "motivation_agent")
    workflow.add_edge("motivation_agent", "strategy_agent")
    workflow.add_edge("strategy_agent", "business_agent")
    workflow.add_edge("business_agent", "application_agent")
    workflow.add_edge("application_agent", "technology_agent")
    workflow.add_edge("technology_agent", END)

    return workflow.compile()


def run_pipeline(system_id: str = "system-demo") -> PipelineState:
    """Execute the full 5-agent pipeline."""
    pipeline = build_multi_agent_pipeline()
    initial_state = {
        "system_id": system_id,
        "messages": [
            HumanMessage(
                content=f"Start modernization ingestion for system '{system_id}'"
            )
        ],
        "processed_layers": [],
        "elements_count": 0,
    }
    return pipeline.invoke(initial_state)


if __name__ == "__main__":
    pipeline = build_multi_agent_pipeline()
    print("==================================================")
    print("5-Subagent Pipeline Graph Architecture:")
    print("==================================================")
    try:
        print(pipeline.get_graph().draw_ascii())
    except Exception:
        print(
            "START -> motivation_agent -> strategy_agent -> business_agent -> application_agent -> technology_agent -> END"
        )
    print("==================================================\n")

    print("Executing 5-Subagent Pipeline...")
    final_state = run_pipeline("system-demo")
    print(f"\n[SUCCESS] Pipeline Execution Complete!")
    print(f"Processed Layers: {final_state['processed_layers']}")
    print(f"Total Model Elements Processed: {final_state['elements_count']}")
    print(
        "\nMulti-Node Trace dispatched to LangSmith under project 'legacy-modernization-mvp'"
    )
