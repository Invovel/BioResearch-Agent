"""Prototype skill input/output contracts."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SkillRequest:
    query: str
    context: dict[str, Any] = field(default_factory=dict)
    available_artifacts: list[str] = field(default_factory=list)
    selected_tools: list[str] = field(default_factory=list)


@dataclass
class SkillResponse:
    skill_name: str
    status: str
    summary: str
    outputs: dict[str, Any] = field(default_factory=dict)
    next_actions: list[str] = field(default_factory=list)

