"""WorkspaceAgent callable facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.agents.base import BasePrototypeAgent
    from agent_langgraph_prototype.skills.registry import build_skill_instances
except ModuleNotFoundError:
    from agent_langgraph_prototype.agents.base import BasePrototypeAgent
    from agent_langgraph_prototype.skills.registry import build_skill_instances


AGENT_NAME = "WorkspaceAgent"
DEFAULT_SKILLS = [
    "ToolDiscoverySkill",
    "PaperEvidenceSkill",
    "TroubleshootingReadbackSkill",
]


class WorkspaceAgent(BasePrototypeAgent):
    agent_name = AGENT_NAME
    default_skills = DEFAULT_SKILLS

    def __init__(self, skills: dict | None = None):
        self.skills = skills or build_skill_instances()

    def get_session_record(self, session_id: str, *, user_id: str | None = None):
        archive = self.skills["ArchiveSkill"]
        response = archive.get_session_record(session_id, user_id=user_id)
        return self._response(
            "workspace agent loaded session record",
            outputs=response.outputs,
            trace=["workspace_agent", "ArchiveSkill.get_session_record"],
            status=response.status,
        )

