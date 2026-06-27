"""Callable archive and memory facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.adapters.archive_adapter import ArchiveAdapter
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.adapters.archive_adapter import ArchiveAdapter
    from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "ArchiveSkill"
KIND = "memory_bundle"


class ArchiveSkill:
    def __init__(self, adapter: ArchiveAdapter | None = None):
        self.adapter = adapter or ArchiveAdapter()

    def archive_session(self, session_data: dict) -> SkillResponse:
        path = self.adapter.archive_session(session_data)
        return SkillResponse(skill_name=SKILL_NAME, status="ok", summary="session archived", outputs={"archive_path": path})

    def get_session_record(self, session_id: str, *, user_id: str | None = None) -> SkillResponse:
        record = self.adapter.get_session_record(session_id, user_id=user_id)
        return SkillResponse(skill_name=SKILL_NAME, status="ok" if record else "not_found", summary="session record lookup complete", outputs={"record": record})

