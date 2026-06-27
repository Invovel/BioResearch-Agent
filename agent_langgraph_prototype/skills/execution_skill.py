"""Callable privileged execution facade."""

from __future__ import annotations

from typing import Any

try:
    from agent_langgraph_prototype.adapters.execution_adapter import ExecutionAdapter
    from agent_langgraph_prototype.adapters.flow_adapter import FlowAdapter
    from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest, SkillResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.adapters.execution_adapter import ExecutionAdapter
    from agent_langgraph_prototype.adapters.flow_adapter import FlowAdapter
    from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest, SkillResponse


SKILL_NAME = "ExecutionSkill"
KIND = "privileged_execution"


class ExecutionSkill:
    def __init__(self, execution_adapter: ExecutionAdapter | None = None, flow_adapter: FlowAdapter | None = None):
        self.execution_adapter = execution_adapter or ExecutionAdapter()
        self.flow_adapter = flow_adapter or FlowAdapter()

    def prepare_query(self, request: SkillRequest) -> SkillResponse:
        prepared = self.flow_adapter.prepare_query(
            request.query,
            available_artifacts=request.available_artifacts,
            model_args_by_flow=request.context.get("model_args_by_flow"),
            top_k=int(request.context.get("top_k") or 5),
            user_id=request.context.get("user_id"),
            session_id=request.context.get("session_id"),
        )
        return SkillResponse(skill_name=SKILL_NAME, status="ok", summary="prepared flow run from query", outputs={"prepared_run": prepared})

    def prepare_flow_plan(self, flow_plan: Any, request: SkillRequest) -> SkillResponse:
        prepared = self.flow_adapter.prepare_flow_plan(
            flow_plan,
            available_artifacts=request.available_artifacts,
            model_args_by_flow=request.context.get("model_args_by_flow"),
            user_id=request.context.get("user_id"),
            session_id=request.context.get("session_id"),
        )
        return SkillResponse(skill_name=SKILL_NAME, status="ok", summary="prepared flow run from flow plan", outputs={"prepared_run": prepared})

    def execute_tool(self, tool_id: str, slide_paths: list[str], *, model_args: dict[str, Any] | None = None, username: str = "bioresearch_agent", extra_slots: dict[str, list[str]] | None = None) -> SkillResponse:
        outputs = self.execution_adapter.execute_tool(
            tool_id,
            slide_paths,
            model_args=model_args,
            username=username,
            extra_slots=extra_slots,
        )
        return SkillResponse(skill_name=SKILL_NAME, status="ok" if outputs.get("success") else "error", summary=f"tool execution attempted for {tool_id}", outputs=outputs)

