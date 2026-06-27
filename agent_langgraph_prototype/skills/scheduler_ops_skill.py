"""Scheduler and ops skill placeholder."""

from __future__ import annotations

from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "SchedulerOpsSkill"
KIND = "ops_bundle"
TOOLS = [
    "scheduler_submit",
    "scheduler_get",
    "scheduler_cancel",
    "scheduler_events",
    "scheduler_local_run_next",
    "ops_cluster_status",
    "ops_jobs_list",
    "ops_job_get",
    "ops_job_events",
    "ops_queue_metrics",
    "ops_quota_summary",
    "ops_metrics_overview",
]


class SchedulerOpsSkill:
    def describe(self) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="scheduler ops catalog skill",
            outputs={"tools": list(TOOLS), "storage_backend": "placeholder"},
        )

