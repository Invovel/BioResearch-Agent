"""Optional LangGraph bridge.

If langgraph is installed, this can build a tiny StateGraph around the same
role-routing logic used by the local fallback graph.
"""

from __future__ import annotations

from dataclasses import asdict

try:
    from agent_langgraph_prototype.contracts.graph_state import PrototypeGraphState
    from agent_langgraph_prototype.framework.graph.local_graph import route_role
except ModuleNotFoundError:
    from agent_langgraph_prototype.contracts.graph_state import PrototypeGraphState
    from agent_langgraph_prototype.framework.graph.local_graph import route_role


def build_langgraph_app():
    try:
        from langgraph.graph import END, START, StateGraph
    except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("langgraph is not installed in this environment") from exc

    def role_router(state: PrototypeGraphState):
        selected_agent, reason = route_role(state.query, state.mode)
        state.selected_agent = selected_agent
        state.route_reason = reason
        state.trace.append(f"role_router:{selected_agent}")
        return state

    graph = StateGraph(PrototypeGraphState)
    graph.add_node("role_router", role_router)
    graph.add_edge(START, "role_router")
    graph.add_edge("role_router", END)
    return graph.compile()


def run_with_langgraph(state: PrototypeGraphState) -> dict:
    app = build_langgraph_app()
    result = app.invoke(state)
    if isinstance(result, PrototypeGraphState):
        return asdict(result)
    if isinstance(result, dict):
        return result
    return {"result": result}


