"""Internal flow harness skill placeholder."""

from __future__ import annotations

from agent_langgraph_prototype.contracts.skill_contracts import SkillResponse


SKILL_NAME = "InternalFlowHarnessSkill"
KIND = "harness_bundle"
TOOLS = [
    "internal_flow_health",
    "internal_flow_prepare",
    "internal_flow_preflight",
    "internal_flow_jobs",
    "internal_flow_fake_runs",
    "internal_flow_manifest_inspection",
    "internal_flow_result_manifest_inspection",
    "internal_flow_executor_state",
    "internal_flow_contract_version",
    "internal_flow_smoke_status",
]


class InternalFlowHarnessSkill:
    def describe(self) -> SkillResponse:
        return SkillResponse(
            skill_name=SKILL_NAME,
            status="ok",
            summary="internal flow harness catalog skill",
            outputs={"tools": list(TOOLS), "status": "placeholder"},
        )

