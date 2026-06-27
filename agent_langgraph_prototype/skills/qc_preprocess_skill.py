"""QC/preprocess skill facade.

This layer is framework-facing. For now it exposes curated tool groups and
delegates read-only tool metadata through ToolDiscoverySkill until dedicated
execution recipes are added.
"""

from __future__ import annotations

try:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "QCPreprocessSkill"
KIND = "tool_bundle"
TOOLS = [
    "29-Summarize-slide-info",
    "30-Get-slide-previews",
    "40-GrandQC",
    "28-Stain-Normalization",
    "52-Global-Macenko",
    "57-estimate-image-spacing",
    "1-foreground-segmentation",
    "48-foreground-segmentation-beta",
]


class QCPreprocessSkill:
    def describe(self) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="qc/preprocess tool bundle",
            outputs={"tools": list(TOOLS)},
        )

