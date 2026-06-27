"""MIL/multimodal skill facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "MILMultimodalSkill"
KIND = "tool_bundle"
TOOLS = [
    "71-Train-MIL-pipeline-from-slides",
    "72-Train-MIL-pipeline-from-h5",
    "73-Infer-MIL-pipeline-for-slides",
    "74-Infer-MIL-pipeline-for-h5",
    "78-Train-MIL-multi-modal-pipeline-from-slides",
    "79-Train-MIL-multi-modal-pipeline-from-h5",
    "80-Infer-MIL-multi-modal-pipeline-for-slides",
    "81-Infer-MIL-multi-modal-pipeline-for-h5",
]


class MILMultimodalSkill:
    def describe(self) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="mil/multimodal tool bundle",
            outputs={"tools": list(TOOLS)},
        )

