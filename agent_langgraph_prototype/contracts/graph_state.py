"""Prototype graph-state contract for isolated agent architecture tests."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PrototypeGraphState:
    query: str
    user_id: str = ""
    session_id: str = ""
    project_id: str = ""
    intent: str = ""
    selected_agent: str = ""
    selected_skills: list[str] = field(default_factory=list)
    available_artifacts: list[str] = field(default_factory=list)
    tool_candidates: list[str] = field(default_factory=list)
    evidence_trace_id: str = ""
    requires_approval: bool = False
    execution_allowed: bool = False
    mode: str = ""
    route_reason: str = ""
    result_summary: dict[str, Any] = field(default_factory=dict)
    trace: list[str] = field(default_factory=list)

