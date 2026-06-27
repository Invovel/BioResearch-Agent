"""Immune/TME skill facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "ImmuneTMESkill"
KIND = "tool_bundle"
TOOLS = [
    "41-Deepliif",
    "48-foreground-segmentation-beta",
    "61-hooknet-tls",
    "66-HistoPlexer",
    "67-GigaTIME",
    "17-lung-tertiary-lymphoid-structures-segmentation",
]


class ImmuneTMESkill:
    def describe(self) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="immune/tme tool bundle",
            outputs={"tools": list(TOOLS)},
        )

