"""Chat/retrieval planning skill for the clean local prototype."""

from __future__ import annotations

from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "ChatPlanningSkill"
KIND = "chat_engine_bundle"
TOOLS = [
    "core.engine.ask",
    "core.engine.prepare_context",
    "retrieval.intent_classifier.classify_intent_with_confidence",
    "retrieval.hybrid_retriever.search_tools",
    "retrieval.hybrid_retriever.search_examples",
]


class ChatPlanningSkill:
    def describe(self) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="chat/retrieval planning skill",
            outputs={"tools": list(TOOLS), "execution_mode": "planning_only_stub"},
        )

    def prepare_context(self, query: str, *, user_type: str | None = None, environment: str = "public") -> SkillResponse:
        outputs = {
            "query": query,
            "user_type": user_type or "researcher",
            "environment": environment,
            "context_blocks": [
                "privacy gate",
                "intent classification",
                "public evidence retrieval",
                "skill/tool catalog lookup",
            ],
            "execution_mode": "no_external_engine",
        }
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="prepared public-safe planning context",
            outputs=outputs,
        )

    def ask(self, query: str, *, user_type: str | None = None, environment: str = "public") -> SkillResponse:
        context = self.prepare_context(query, user_type=user_type, environment=environment).outputs
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="generated reviewable planning response",
            outputs={
                "answer": "This is a planning-only response. Attach public evidence and human review before using it.",
                "context": context,
            },
        )

