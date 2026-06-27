"""ExecutionAgent callable facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.agents.base import BasePrototypeAgent
    from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest
    from agent_langgraph_prototype.skills.registry import build_skill_instances
except ModuleNotFoundError:
    from agent_langgraph_prototype.agents.base import BasePrototypeAgent
    from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest
    from agent_langgraph_prototype.skills.registry import build_skill_instances


AGENT_NAME = "ExecutionAgent"
DEFAULT_SKILLS = [
    "ExecutionSkill",
    "TroubleshootingReadbackSkill",
    "AnnotationPrepSkill",
]


class ExecutionAgent(BasePrototypeAgent):
    agent_name = AGENT_NAME
    default_skills = DEFAULT_SKILLS

    def __init__(self, skills: dict | None = None):
        self.skills = skills or build_skill_instances()

    def prepare(self, query: str, *, available_artifacts: list[str] | None = None, model_args_by_flow: dict | None = None):
        execution = self.skills["ExecutionSkill"]
        request = SkillRequest(
            query=query,
            available_artifacts=list(available_artifacts or []),
            context={"model_args_by_flow": model_args_by_flow or {}},
        )
        response = execution.prepare_query(request)
        return self._response(
            "execution agent prepared run",
            outputs=response.outputs,
            trace=["execution_agent", "ExecutionSkill.prepare_query"],
            status=response.status,
        )

