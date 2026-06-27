"""Compatibility alias to the active framework graph topology."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.framework.graph.topology import GRAPH as GRAPH_TOPOLOGY
except ModuleNotFoundError:
    from agent_langgraph_prototype.framework.graph.topology import GRAPH as GRAPH_TOPOLOGY

