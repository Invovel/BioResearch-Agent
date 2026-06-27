"""ResearchAgent callable facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.agents.base import BasePrototypeAgent
    from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest
    from agent_langgraph_prototype.skills.registry import build_skill_instances
except ModuleNotFoundError:
    from agent_langgraph_prototype.agents.base import BasePrototypeAgent
    from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest
    from agent_langgraph_prototype.skills.registry import build_skill_instances


AGENT_NAME = "ResearchAgent"
DEFAULT_SKILLS = [
    "PaperEvidenceSkill",
    "ImmuneTMESkill",
    "MILMultimodalSkill",
    "NucleusPathomicsSkill",
]


class ResearchAgent(BasePrototypeAgent):
    agent_name = AGENT_NAME
    default_skills = DEFAULT_SKILLS

    def __init__(self, skills: dict | None = None):
        self.skills = skills or build_skill_instances()

    def search_papers(self, query: str, *, source: str = "all", top_k: int = 10):
        paper = self.skills["PaperEvidenceSkill"]
        request = SkillRequest(query=query, context={"source": source, "top_k": top_k})
        response = paper.search(request)
        return self._response(
            "research agent paper search complete",
            outputs=response.outputs,
            trace=["research_agent", "PaperEvidenceSkill.search"],
            status=response.status,
        )

