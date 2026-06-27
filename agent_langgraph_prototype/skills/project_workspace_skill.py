"""Project workspace skill placeholder."""

from __future__ import annotations

from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "ProjectWorkspaceSkill"
KIND = "workspace_bundle"
TOOLS = [
    "project_create",
    "project_list",
    "project_update",
    "project_delete",
    "project_pin",
    "project_archive",
    "project_scan",
    "project_materials",
    "project_sessions_bind",
    "project_sessions_unbind",
    "project_paper_folders_bind",
    "project_paper_folders_unbind",
    "project_session_map",
    "asset_upload",
    "asset_download",
]


class ProjectWorkspaceSkill:
    def describe(self) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="project workspace catalog skill",
            outputs={"tools": list(TOOLS), "execution_mode": "placeholder_no_private_assets"},
        )

