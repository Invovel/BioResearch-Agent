"""Public-safe flow planning stub."""

from __future__ import annotations

import hashlib
from typing import Any


class FlowAdapter:
    def __init__(self):
        self._prepared_runs: dict[str, dict[str, Any]] = {}

    def plan(self, query: str, *, available_artifacts: list[str] | None = None, top_k: int = 5) -> dict[str, Any]:
        artifacts = list(available_artifacts or [])
        return {
            "query": query,
            "top_k": top_k,
            "available_artifacts": artifacts,
            "candidate_steps": [
                "classify intent",
                "select bounded skill",
                "inspect catalog-only tool metadata",
                "prepare human review packet",
            ],
            "execution_mode": "planning_only_stub",
        }

    def prepare_query(
        self,
        query: str,
        *,
        available_artifacts: list[str] | None = None,
        model_args_by_flow: dict[str, dict[str, Any]] | None = None,
        top_k: int = 5,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        plan = self.plan(query, available_artifacts=available_artifacts, top_k=top_k)
        return self.prepare_flow_plan(
            plan,
            available_artifacts=available_artifacts,
            model_args_by_flow=model_args_by_flow,
            user_id=user_id,
            session_id=session_id,
        )

    def prepare_flow_plan(
        self,
        flow_plan: Any,
        *,
        available_artifacts: list[str] | None = None,
        model_args_by_flow: dict[str, dict[str, Any]] | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "flow_plan": flow_plan,
            "available_artifacts": list(available_artifacts or []),
            "model_args_keys": sorted((model_args_by_flow or {}).keys()),
            "user_id": user_id or "",
            "session_id": session_id or "",
            "status": "prepared_for_review",
            "execution_mode": "no_execution",
        }
        run_hash = hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()[:16]
        payload["run_hash"] = run_hash
        self._prepared_runs[run_hash] = payload
        return payload

    def get_prepared_run(self, run_hash: str) -> dict[str, Any] | None:
        return self._prepared_runs.get(run_hash)

