"""Callable ToolDiscoverySkill facade."""

from __future__ import annotations

try:
    from agent_langgraph_prototype.adapters.flow_adapter import FlowAdapter
    from agent_langgraph_prototype.adapters.tool_registry_adapter import ToolRegistryAdapter
    from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest, SkillResponse
except ModuleNotFoundError:
    from agent_langgraph_prototype.adapters.flow_adapter import FlowAdapter
    from agent_langgraph_prototype.adapters.tool_registry_adapter import ToolRegistryAdapter
    from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest, SkillResponse


SKILL_NAME = "ToolDiscoverySkill"
KIND = "read_only"


class ToolDiscoverySkill:
    def __init__(self, tool_adapter: ToolRegistryAdapter | None = None, flow_adapter: FlowAdapter | None = None):
        self.tool_adapter = tool_adapter or ToolRegistryAdapter()
        self.flow_adapter = flow_adapter or FlowAdapter()

    def manifest_summary(self) -> SkillResponse:
        data = self.tool_adapter.manifest_summary()
        return SkillResponse(skill_name=SKILL_NAME, status="ok", summary=f"loaded {len(data)} tools", outputs={"tools": data})

    def tool_detail(self, tool_id: str) -> SkillResponse:
        data = self.tool_adapter.tool_detail(tool_id)
        return SkillResponse(skill_name=SKILL_NAME, status="ok" if data else "not_found", summary=f"tool detail for {tool_id}", outputs={"tool": data})

    def tool_io_spec(self, tool_id: str) -> SkillResponse:
        data = self.tool_adapter.tool_io_spec(tool_id)
        return SkillResponse(skill_name=SKILL_NAME, status="ok" if data else "not_found", summary=f"io spec for {tool_id}", outputs={"io_spec": data})

    def compatibility(self, from_tool: str, from_output: str, to_tool: str, to_input: str) -> SkillResponse:
        data = self.tool_adapter.tool_compatibility(from_tool, from_output, to_tool, to_input)
        return SkillResponse(skill_name=SKILL_NAME, status="ok", summary="compatibility checked", outputs={"compatibility": data})

    def flow_plan_debug(self, request: SkillRequest) -> SkillResponse:
        plan = self.flow_adapter.plan(
            request.query,
            available_artifacts=request.available_artifacts,
            top_k=int(request.context.get("top_k") or 5),
        )
        return SkillResponse(skill_name=SKILL_NAME, status="ok", summary="flow plan prepared", outputs={"flow_plan": plan})

