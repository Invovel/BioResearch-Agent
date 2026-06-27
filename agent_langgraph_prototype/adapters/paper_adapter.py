"""Public paper-evidence adapter stub."""

from __future__ import annotations

from typing import Any


class PaperAdapter:
    def search(
        self,
        query: str,
        *,
        source: str = "all",
        days: int | None = None,
        top_k: int = 10,
        advanced_query: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "query": query,
            "source": source,
            "days": days,
            "top_k": top_k,
            "advanced_query_keys": sorted((advanced_query or {}).keys()),
            "results": [],
            "status": "stub_no_external_search",
        }

    def stats(self) -> dict[str, Any]:
        return {"status": "stub", "public_cache_records": 0}

    def daily_recommendations(self, *, pubmed_limit: int = 2, arxiv_limit: int = 2) -> dict[str, Any]:
        return {
            "status": "stub",
            "recommendations": [],
            "limits": {"pubmed": pubmed_limit, "arxiv": arxiv_limit},
        }

    def analyze(self, *, doi: str = "", title: str = "", abstract: str = "", source: str = "unknown", fast: bool = False) -> dict[str, Any]:
        return {
            "status": "stub_review_required",
            "doi": doi,
            "title": title,
            "source": source,
            "fast": fast,
            "summary": "Paper analysis placeholder; attach a public implementation before using for claims.",
            "abstract_length": len(abstract),
        }

    def plan_toolchain(
        self,
        query: str,
        paper_context: Any,
        *,
        include_execution_readiness: bool = False,
        available_artifacts: list[str] | None = None,
        folder_id: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        project_id: str | None = None,
        project_name: str | None = None,
    ) -> dict[str, Any]:
        return {
            "query": query,
            "paper_context_present": bool(paper_context),
            "include_execution_readiness": include_execution_readiness,
            "available_artifacts": list(available_artifacts or []),
            "scope": {
                "folder_id": folder_id or "",
                "user_id": user_id or "",
                "session_id": session_id or "",
                "project_id": project_id or "",
                "project_name": project_name or "",
            },
            "steps": ["extract public claims", "map to candidate skills", "require human review"],
            "execution_mode": "planning_only_stub",
        }

