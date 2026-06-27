"""Agent contracts for the prototype runtime."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResponse:
    agent_name: str
    status: str
    summary: str
    outputs: dict[str, Any] = field(default_factory=dict)
    trace: list[str] = field(default_factory=list)


