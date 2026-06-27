"""Annotation/prep skill facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "AnnotationPrepSkill"
KIND = "tool_bundle"
TOOLS = [
    "23-SAM-point-annotation",
    "24-SAM2.1-point-annotation",
    "25-BiomedParse",
    "31-Summarize-asap-xml-info",
    "32-Transfer-asap-xml-to-tif",
    "33-Generate-segmentation-patches",
    "34-Generate-classification-patches",
    "38-Text-Encoding",
    "54-kfb2svs",
    "55-pkl2h5",
    "56-image2tif",
    "58-value-mapping",
    "59-generate-overlays",
]


class AnnotationPrepSkill:
    def describe(self) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="annotation and preprocessing tool bundle",
            outputs={"tools": list(TOOLS)},
        )

