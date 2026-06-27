"""Nucleus/pathomics skill facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "NucleusPathomicsSkill"
KIND = "tool_bundle"
TOOLS = [
    "4-nucleus-segmentation-hovernet-pannuke",
    "50-hovernet-pannuke-mp",
    "53-hover-next-mp",
    "49-slide-embedding-all-methods",
    "76-Pathomics-pipeline-from-slides",
    "77-Pathomics-pipeline-from-slides-nucleus",
]


class NucleusPathomicsSkill:
    def describe(self) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="nucleus/pathomics tool bundle",
            outputs={"tools": list(TOOLS)},
        )

