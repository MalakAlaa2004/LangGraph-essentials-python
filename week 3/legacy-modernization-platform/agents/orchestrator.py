import os
import sys
from typing import List, Optional, TypedDict
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

from langgraph.graph import END, START, StateGraph

from agents.strategy_analyst_agent import StrategyAnalystAgent
from agents.business_analyst_agent import BusinessAnalystAgent
from agents.codebase_analyst_agent import CodebaseAnalystAgent
from agents.infra_analyst_agent import InfraAnalystAgent
from agents.data_analyst_agent import DataAnalystAgent
from agents.reconciler_agent import ReconcilerAgent
from agents.validator_agent import ValidatorAgent


class OrchestratorState(TypedDict):
    system_id: str
    status: str
    steps_completed: List[str]


def create_orchestrator_step(step_name: str):
    def node_fn(state: OrchestratorState) -> OrchestratorState:
        completed = list(state.get("steps_completed", []))
        completed.append(step_name)
        return {
            "system_id": state["system_id"],
            "status": f"in_progress:{step_name}",
            "steps_completed": completed,
        }

    return node_fn


def build_phase1_orchestrator():
    """Build master LangGraph StateGraph orchestrator for Phase 1 MVP."""
    workflow = StateGraph(OrchestratorState)

    # 1. Add all specialized subagent nodes
    workflow.add_node("strategy_analyst", create_orchestrator_step("strategy_analyst"))
    workflow.add_node("business_analyst", create_orchestrator_step("business_analyst"))
    workflow.add_node("codebase_analyst", create_orchestrator_step("codebase_analyst"))
    workflow.add_node("infra_analyst", create_orchestrator_step("infra_analyst"))
    workflow.add_node("data_analyst", create_orchestrator_step("data_analyst"))
    workflow.add_node("reconciler", create_orchestrator_step("reconciler"))
    workflow.add_node("validator", create_orchestrator_step("validator"))

    # 2. Wire pipeline sequentially
    workflow.add_edge(START, "strategy_analyst")
    workflow.add_edge("strategy_analyst", "business_analyst")
    workflow.add_edge("business_analyst", "codebase_analyst")
    workflow.add_edge("codebase_analyst", "infra_analyst")
    workflow.add_edge("infra_analyst", "data_analyst")
    workflow.add_edge("data_analyst", "reconciler")
    workflow.add_edge("reconciler", "validator")
    workflow.add_edge("validator", END)

    return workflow.compile()


def run_orchestration(system_id: str = "system-demo") -> OrchestratorState:
    orchestrator = build_phase1_orchestrator()
    initial_state: OrchestratorState = {
        "system_id": system_id,
        "status": "started",
        "steps_completed": [],
    }
    final_state = orchestrator.invoke(initial_state)
    return final_state


if __name__ == "__main__":
    orchestrator = build_phase1_orchestrator()
    print("==================================================")
    print("Top-Level Phase 1 Orchestrator Graph Architecture:")
    print("==================================================")
    try:
        print(orchestrator.get_graph().draw_ascii())
    except Exception:
        print(
            "START -> strategy -> business -> codebase -> infra -> data -> reconciler -> validator -> END"
        )
    print("==================================================\n")

    print("Executing Top-Level Phase 1 Orchestration Pipeline...\n")
    res = run_orchestration("system-demo")
    print(f"[SUCCESS] Orchestration Completed for System '{res['system_id']}':")
    print(
        f" - Steps Executed ({len(res['steps_completed'])}): {res['steps_completed']}"
    )
    print("\nTrace dispatched to LangSmith under project 'legacy-modernization-mvp'")
