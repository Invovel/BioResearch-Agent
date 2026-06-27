"""Minimal local graph executor for the isolated prototype.

This keeps the prototype usable even when langgraph is not installed.
"""

from __future__ import annotations

from dataclasses import asdict

try:
    from agent_langgraph_prototype.contracts.graph_state import PrototypeGraphState
    from agent_langgraph_prototype.framework.router.role_router import ROLE_ROUTING_POLICY
except ModuleNotFoundError:
    from agent_langgraph_prototype.contracts.graph_state import PrototypeGraphState
    from agent_langgraph_prototype.framework.router.role_router import ROLE_ROUTING_POLICY


def route_role(query: str, mode: str = "") -> tuple[str, str]:
    q = str(query or "").lower()
    if mode in {"execute_tool", "prepare_query", "prepare_flow_plan", "inspect_manifest", "locate_result_file"}:
        return "execution_agent", "mode_execution"
    if mode in {"paper_search", "paper_stats", "paper_analyze", "paper_toolchain"}:
        return "research_agent", "mode_research"
    if mode in {"archive_session", "get_session_record"}:
        return "workspace_agent", "mode_workspace"

    for item in ROLE_ROUTING_POLICY["execution_keywords"]:
        if item.lower() in q:
            return "execution_agent", f"keyword:{item}"
    for item in ROLE_ROUTING_POLICY["research_keywords"]:
        if item.lower() in q:
            return "research_agent", f"keyword:{item}"
    for item in ROLE_ROUTING_POLICY["workspace_keywords"]:
        if item.lower() in q:
            return "workspace_agent", f"keyword:{item}"
    for item in ROLE_ROUTING_POLICY["planner_keywords"]:
        if item.lower() in q:
            return "planner_agent", f"keyword:{item}"
    return "planner_agent", "default_planner"


class LocalPrototypeGraph:
    def run(self, state: PrototypeGraphState) -> PrototypeGraphState:
        selected_agent, reason = route_role(state.query, state.mode)
        state.selected_agent = selected_agent
        state.route_reason = reason
        state.trace.append(f"role_router:{selected_agent}")
        return state

    def run_dict(self, state: PrototypeGraphState) -> dict:
        result = self.run(state)
        return asdict(result)


