"""Alias entry for graph-state contract."""

try:
    from agent_langgraph_prototype.contracts.graph_state import PrototypeGraphState
except ModuleNotFoundError:
    from agent_langgraph_prototype.contracts.graph_state import PrototypeGraphState

__all__ = ["PrototypeGraphState"]

