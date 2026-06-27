"""Segmentation/detection skill facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "SegmentationDetectionSkill"
KIND = "tool_bundle"
TOOLS = [
    "2-lung-cancer-segmentation",
    "3-tissue-segmentation",
    "11-CD34-vessel-segmentation",
    "12-PAS-kidney-glomeruli-segmentation",
    "13-intrahepatic-cholangiocarcinoma-tissue-segmentation",
    "16-liver-tissue-segmentation",
    "17-lung-tertiary-lymphoid-structures-segmentation",
    "18-PAS-kidney-glomeruli-multi-class-segmentation",
    "26-Kidney-Masson-4-class-segmentation",
    "35-Train-segmentation-baseline",
    "36-Infer-segmentation-baseline",
    "60-tissue-segmentation-trial",
    "64-TUZI",
    "68-Train-segmentation-pipeline-from-slides-xml",
    "69-Train-segmentation-pipeline-from-slides-mask",
    "70-Infer-segmentation-pipeline",
    "5-pancreas-tumor-detection",
    "6-breast-tumor-detection",
    "7-gastric-tumor-detection",
    "8-colon-tumor-detection",
    "9-endometrium-tumor-detection",
    "10-ovarian-tumor-detection",
    "14-intrahepatic-cholangiocarcinoma-cancer-detection",
    "51-ssl-luad-classification",
    "62-pancancer-detection-20",
    "63-pancancer-detection-40",
    "75-Gleason-AGGC",
]


class SegmentationDetectionSkill:
    def describe(self) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="segmentation and detection tool bundle",
            outputs={"tools": list(TOOLS)},
        )

