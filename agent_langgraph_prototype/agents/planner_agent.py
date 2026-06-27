"""PlannerAgent callable facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.agents.base import BasePrototypeAgent
    from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest
    from agent_langgraph_prototype.skills.registry import build_skill_instances
except ModuleNotFoundError:
    from agent_langgraph_prototype.agents.base import BasePrototypeAgent
    from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest
    from agent_langgraph_prototype.skills.registry import build_skill_instances


AGENT_NAME = "PlannerAgent"
DEFAULT_SKILLS = [
    "ToolDiscoverySkill",
    "QCPreprocessSkill",
    "SegmentationDetectionSkill",
    "NucleusPathomicsSkill",
]


class PlannerAgent(BasePrototypeAgent):
    agent_name = AGENT_NAME
    default_skills = DEFAULT_SKILLS

    def __init__(self, skills: dict | None = None):
        self.skills = skills or build_skill_instances()

    def plan(self, query: str, *, available_artifacts: list[str] | None = None, top_k: int = 5):
        discovery = self.skills["ToolDiscoverySkill"]
        request = SkillRequest(
            query=query,
            available_artifacts=list(available_artifacts or []),
            context={"top_k": top_k},
        )
        response = discovery.flow_plan_debug(request)
        return self._response(
            "planner agent produced flow plan",
            outputs=response.outputs,
            trace=["planner_agent", "ToolDiscoverySkill.flow_plan_debug"],
            status=response.status,
        )

