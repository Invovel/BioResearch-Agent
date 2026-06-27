"""Callable PaperEvidenceSkill facade."""

from __future__ import annotations

from typing import Any

try:
    from agent_langgraph_prototype.adapters.paper_adapter import PaperAdapter
    from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest, SkillResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.adapters.paper_adapter import PaperAdapter
    from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest, SkillResponse


SKILL_NAME = "PaperEvidenceSkill"
KIND = "service_bundle"


class PaperEvidenceSkill:
    def __init__(self, adapter: PaperAdapter | None = None):
        self.adapter = adapter or PaperAdapter()

    def search(self, request: SkillRequest) -> SkillResponse:
        outputs = self.adapter.search(
            request.query,
            source=str(request.context.get("source") or "all"),
            days=request.context.get("days"),
            top_k=int(request.context.get("top_k") or 10),
            advanced_query=request.context.get("advanced_query"),
        )
        return SkillResponse(skill_name=SKILL_NAME, status="ok", summary="paper search complete", outputs=outputs)

    def stats(self) -> SkillResponse:
        outputs = self.adapter.stats()
        return SkillResponse(skill_name=SKILL_NAME, status="ok", summary="paper stats loaded", outputs=outputs)

    def analyze(self, *, doi: str = "", title: str = "", abstract: str = "", source: str = "unknown", fast: bool = False) -> SkillResponse:
        outputs = self.adapter.analyze(doi=doi, title=title, abstract=abstract, source=source, fast=fast)
        return SkillResponse(skill_name=SKILL_NAME, status="ok", summary="paper analysis complete", outputs=outputs)

    def plan_toolchain(self, request: SkillRequest, *, paper_context: Any) -> SkillResponse:
        trace = self.adapter.plan_toolchain(
            request.query,
            paper_context,
            include_execution_readiness=bool(request.context.get("include_execution_readiness")),
            available_artifacts=request.available_artifacts,
            folder_id=request.context.get("folder_id"),
            user_id=request.context.get("user_id"),
            session_id=request.context.get("session_id"),
            project_id=request.context.get("project_id"),
            project_name=request.context.get("project_name"),
        )
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="paper toolchain trace prepared",
            outputs={"trace": trace.to_dict() if hasattr(trace, "to_dict") else trace},
        )

