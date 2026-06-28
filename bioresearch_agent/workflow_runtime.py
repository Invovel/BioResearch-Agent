from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .privacy import PrivacyGate
from .schemas import SkillWorkflowSpec, ToolResult
from .tools import ToolRegistry


@dataclass(frozen=True)
class WorkflowRunResult:
    workflow_id: str
    skill_id: str
    status: str
    node_results: tuple[dict[str, Any], ...]
    tool_results: tuple[ToolResult, ...]
    context_keys: tuple[str, ...]


class SkillWorkflowRuntime:
    """Small LangGraph-style runtime for skill-owned workflow/tool bundles."""

    def __init__(self, *, tools: ToolRegistry, privacy_gate: PrivacyGate | None = None) -> None:
        self.tools = tools
        self.privacy_gate = privacy_gate or PrivacyGate()

    def run(
        self,
        workflow: SkillWorkflowSpec,
        payload: dict[str, Any],
        *,
        confirmed: bool = False,
    ) -> WorkflowRunResult:
        context = dict(payload)
        nodes = {str(node["node_id"]): node for node in workflow.nodes}
        node_results: list[dict[str, Any]] = []
        tool_results: list[ToolResult] = []
        status = "ok"

        for node_id in _topological_order(nodes, workflow.edges):
            node = nodes[node_id]
            kind = str(node.get("kind", ""))
            if kind == "gate":
                result = self._run_gate(node_id, context)
            elif kind == "tool":
                result, tool_result = self._run_tool(node_id, node, context, confirmed=confirmed)
                if tool_result is not None:
                    tool_results.append(tool_result)
            elif kind in {"skill", "memory"}:
                result = {"node_id": node_id, "kind": kind, "status": "ok", "note": "Handled by skill handler or memory trace layer."}
            else:
                result = {"node_id": node_id, "kind": kind, "status": "skipped", "note": "Unknown node kind."}

            if result["status"] in {"failed", "skipped", "needs_confirmation"} and status == "ok":
                status = result["status"]
            node_results.append(result)

        return WorkflowRunResult(
            workflow_id=workflow.workflow_id,
            skill_id=workflow.skill_id,
            status=status,
            node_results=tuple(node_results),
            tool_results=tuple(tool_results),
            context_keys=tuple(sorted(context)),
        )

    def _run_gate(self, node_id: str, context: dict[str, Any]) -> dict[str, Any]:
        try:
            self.privacy_gate.assert_public_safe(str(context))
        except ValueError as exc:
            return {"node_id": node_id, "kind": "gate", "status": "failed", "note": str(exc)}
        return {"node_id": node_id, "kind": "gate", "status": "ok"}

    def _run_tool(
        self,
        node_id: str,
        node: dict[str, Any],
        context: dict[str, Any],
        *,
        confirmed: bool,
    ) -> tuple[dict[str, Any], ToolResult | None]:
        tool_id = str(node.get("tool_id") or node_id)
        spec = self.tools.get_spec(tool_id)
        if spec is None:
            tool_result = self.tools.run(tool_id, context, confirmed=confirmed)
            return {"node_id": node_id, "kind": "tool", "tool_id": tool_id, "status": tool_result.status, "note": "Tool not registered."}, tool_result

        missing_inputs = tuple(key for key in spec.required_inputs if key not in context)
        if missing_inputs:
            tool_result = ToolResult(
                tool_id=tool_id,
                status="skipped",
                warnings=(f"Missing required workflow inputs: {', '.join(missing_inputs)}.",),
            )
            return {
                "node_id": node_id,
                "kind": "tool",
                "tool_id": tool_id,
                "status": "skipped",
                "missing_inputs": missing_inputs,
            }, tool_result

        tool_result = self.tools.run(tool_id, context, confirmed=confirmed)
        if tool_result.status == "ok":
            missing_outputs = tuple(key for key in spec.produced_outputs if key not in tool_result.output)
            if missing_outputs:
                tool_result = ToolResult(
                    tool_id=tool_id,
                    status="failed",
                    output=tool_result.output,
                    warnings=(f"Tool omitted declared outputs: {', '.join(missing_outputs)}.",),
                )
            else:
                context.update(tool_result.output)
        return {"node_id": node_id, "kind": "tool", "tool_id": tool_id, "status": tool_result.status}, tool_result


def _topological_order(nodes: dict[str, dict[str, Any]], edges: tuple[tuple[str, str], ...]) -> tuple[str, ...]:
    incoming = {node_id: 0 for node_id in nodes}
    outgoing: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    for source, target in edges:
        if source not in nodes or target not in nodes:
            continue
        incoming[target] += 1
        outgoing[source].append(target)

    ready = [node_id for node_id, count in incoming.items() if count == 0]
    ordered: list[str] = []
    while ready:
        node_id = ready.pop(0)
        ordered.append(node_id)
        for target in outgoing[node_id]:
            incoming[target] -= 1
            if incoming[target] == 0:
                ready.append(target)
    if len(ordered) != len(nodes):
        return tuple(nodes)
    return tuple(ordered)
