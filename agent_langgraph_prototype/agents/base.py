"""Base helpers for callable prototype agents."""

from __future__ import annotations

from typing import Iterable

try:
    from agent_langgraph_prototype.contracts.agent_contracts import AgentResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.contracts.agent_contracts import AgentResponse


class BasePrototypeAgent:
    agent_name = "BasePrototypeAgent"
    default_skills: list[str] = []

    def describe(self) -> dict:
        return {
            "agent": self.agent_name,
            "skills": list(self.default_skills),
        }

    def _response(self, summary: str, *, outputs=None, trace=None, status: str = "ok") -> AgentResponse:
        return AgentResponse(
            agent_name=self.agent_name,
            status=status,
            summary=summary,
            outputs=dict(outputs or {}),
            trace=list(trace or []),
        )

