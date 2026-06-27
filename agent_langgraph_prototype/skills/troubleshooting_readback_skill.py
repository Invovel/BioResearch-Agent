"""Callable readback and troubleshooting facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.adapters.execution_adapter import ExecutionAdapter
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.adapters.execution_adapter import ExecutionAdapter
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "TroubleshootingReadbackSkill"
KIND = "readback_bundle"


class TroubleshootingReadbackSkill:
    def __init__(self, adapter: ExecutionAdapter | None = None):
        self.adapter = adapter or ExecutionAdapter()

    def inspect_manifest(self, manifest_path: str) -> SkillResponse:
        manifest = self.adapter.inspect_result_manifest(manifest_path)
        return SkillResponse(skill_name=SKILL_NAME, status="ok", summary="manifest loaded", outputs={"manifest": manifest})

    def locate_result_file(self, task_id: str, filename: str, *, username: str = "bioresearch_agent") -> SkillResponse:
        path = self.adapter.find_result_file(task_id, filename, username=username)
        return SkillResponse(skill_name=SKILL_NAME, status="ok" if path else "not_found", summary="result file lookup complete", outputs={"path": path})

