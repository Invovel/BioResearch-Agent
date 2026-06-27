"""Upload and recovery skill facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse

try:
    from agent_langgraph_prototype.runtime_config import get_runtime_config
except ModuleNotFoundError:
    from agent_langgraph_prototype.runtime_config import get_runtime_config


SKILL_NAME = "UploadRecoverySkill"
KIND = "io_bundle"
TOOLS = [
    "upload_file",
    "upload_chunk_init",
    "upload_chunk_save",
    "upload_chunk_complete",
    "upload_recover",
    "uploaded_file_download",
    "uploaded_file_preview",
]


class UploadRecoverySkill:
    def __init__(self):
        self.runtime = get_runtime_config()

    def describe(self) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="upload recovery skill",
            outputs={"tools": list(TOOLS), "upload_root": str(self.runtime.data_root / "uploads")},
        )

