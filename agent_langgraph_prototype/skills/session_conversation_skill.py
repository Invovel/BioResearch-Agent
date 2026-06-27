"""Session and conversation skill placeholder."""

from __future__ import annotations

from uuid import uuid4

from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "SessionConversationSkill"
KIND = "session_bundle"
TOOLS = [
    "session_bootstrap",
    "session_new",
    "session_history",
    "session_reset",
    "session_archive",
    "session_archive_user_index",
    "conversation_list",
    "conversation_get",
    "conversation_patch",
    "conversation_add_message",
]


class SessionConversationSkill:
    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def describe(self) -> SkillResponse:
        return SkillResponse(skill_name=SKILL_NAME, status="ok", summary="session and conversation skill", outputs={"tools": list(TOOLS)})

    def session_new(self, *, user_id: str = "") -> SkillResponse:
        session_id = uuid4().hex
        payload = {"session_id": session_id, "user_id": user_id, "messages": []}
        self._sessions[session_id] = payload
        return SkillResponse(skill_name=SKILL_NAME, status="ok", summary="synthetic session created", outputs=payload)

    def session_history(self, session_id: str) -> SkillResponse:
        history = self._sessions.get(session_id)
        return SkillResponse(skill_name=SKILL_NAME, status="ok" if history else "not_found", summary="session history loaded", outputs={"history": history})

    def session_reset(self, session_id: str) -> SkillResponse:
        ok = session_id in self._sessions
        if ok:
            self._sessions[session_id]["messages"] = []
        return SkillResponse(skill_name=SKILL_NAME, status="ok" if ok else "not_found", summary="session reset", outputs={"reset": ok})

    def session_archive(self, session_id: str) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="placeholder",
            summary="archive requires the ArchiveSkill placeholder",
            outputs={"session_id": session_id, "execution_mode": "placeholder"},
        )

