"""Clean local orchestrator for the BioResearch-Agent prototype."""

from __future__ import annotations

from typing import Any

from agent_langgraph_prototype.agents.roles import build_agent_instances
from agent_langgraph_prototype.contracts.graph_state import PrototypeGraphState
from agent_langgraph_prototype.contracts.skill_contracts import SkillRequest
from agent_langgraph_prototype.framework.graph.langgraph_bridge import run_with_langgraph
from agent_langgraph_prototype.framework.graph.local_graph import LocalPrototypeGraph
from agent_langgraph_prototype.runtime_config import get_runtime_config
from agent_langgraph_prototype.skills.archive_skill import ArchiveSkill
from agent_langgraph_prototype.skills.chat_planning_skill import ChatPlanningSkill
from agent_langgraph_prototype.skills.discovery_skill import ToolDiscoverySkill
from agent_langgraph_prototype.skills.execution_skill import ExecutionSkill
from agent_langgraph_prototype.skills.paper_evidence_skill import PaperEvidenceSkill
from agent_langgraph_prototype.skills.troubleshooting_readback_skill import TroubleshootingReadbackSkill


class PrototypeOrchestrator:
    def __init__(self):
        self.runtime = get_runtime_config()
        self.local_graph = LocalPrototypeGraph()
        self.agents = build_agent_instances()
        self.chat = ChatPlanningSkill()
        self.discovery = ToolDiscoverySkill()
        self.paper = PaperEvidenceSkill()
        self.execution = ExecutionSkill()
        self.readback = TroubleshootingReadbackSkill()
        self.archive = ArchiveSkill()

    def info(self) -> dict[str, str]:
        return {
            "runtime_root": str(self.runtime.runtime_root),
            "data_root": str(self.runtime.data_root),
            "exec_base": str(self.runtime.exec_base),
            "archive_root": str(self.runtime.archive_root),
            "traces_root": str(self.runtime.traces_root),
            "execution_mode": "local_stub_only",
        }

    def _graph_trace(self, graph_state: PrototypeGraphState, graph_backend: str) -> dict[str, Any]:
        if graph_backend == "langgraph":
            try:
                return run_with_langgraph(graph_state)
            except RuntimeError as exc:
                self.local_graph.run(graph_state)
                return {"fallback": "local", "error": str(exc), "trace": list(graph_state.trace)}
        self.local_graph.run(graph_state)
        return {
            "selected_agent": graph_state.selected_agent,
            "route_reason": graph_state.route_reason,
            "trace": list(graph_state.trace),
        }

    def run(self, query: str = "", *, mode: str = "tool_manifest", **kwargs) -> dict[str, Any]:
        graph_backend = str(kwargs.get("graph_backend") or "local").strip().lower()
        graph_state = PrototypeGraphState(
            query=query,
            user_id=str(kwargs.get("user_id") or ""),
            session_id=str(kwargs.get("session_id") or ""),
            project_id=str(kwargs.get("project_id") or ""),
            available_artifacts=list(kwargs.get("available_artifacts") or []),
            mode=mode,
        )
        graph_trace = self._graph_trace(graph_state, graph_backend)
        request = SkillRequest(
            query=query,
            context=dict(kwargs.get("context") or {}),
            available_artifacts=list(kwargs.get("available_artifacts") or []),
            selected_tools=list(kwargs.get("selected_tools") or []),
        )

        if mode == "tool_manifest":
            return {"graph": graph_trace, **self.discovery.manifest_summary().outputs}
        if mode == "chat_prepare":
            return {"graph": graph_trace, **self.chat.prepare_context(query).outputs}
        if mode == "chat_ask":
            return {"graph": graph_trace, **self.chat.ask(query).outputs}
        if mode == "tool_detail":
            return {"graph": graph_trace, **self.discovery.tool_detail(str(kwargs.get("tool_id") or "")).outputs}
        if mode == "tool_io_spec":
            return {"graph": graph_trace, **self.discovery.tool_io_spec(str(kwargs.get("tool_id") or "")).outputs}
        if mode == "tool_compatibility":
            return {
                "graph": graph_trace,
                **self.discovery.compatibility(
                    str(kwargs.get("from_tool") or ""),
                    str(kwargs.get("from_output") or ""),
                    str(kwargs.get("to_tool") or ""),
                    str(kwargs.get("to_input") or ""),
                ).outputs,
            }
        if mode == "flow_plan":
            response = self.agents["PlannerAgent"].plan(
                query,
                available_artifacts=request.available_artifacts,
                top_k=int(request.context.get("top_k") or 5),
            )
            return {"graph": graph_trace, **response.outputs}
        if mode == "paper_search":
            response = self.agents["ResearchAgent"].search_papers(
                query,
                source=str(request.context.get("source") or "all"),
                top_k=int(request.context.get("top_k") or 10),
            )
            return {"graph": graph_trace, **response.outputs}
        if mode == "paper_stats":
            return {"graph": graph_trace, **self.paper.stats().outputs}
        if mode == "paper_analyze":
            return {
                "graph": graph_trace,
                **self.paper.analyze(
                    doi=str(kwargs.get("doi") or ""),
                    title=str(kwargs.get("title") or ""),
                    abstract=str(kwargs.get("abstract") or ""),
                    source=str(kwargs.get("source") or "unknown"),
                    fast=bool(kwargs.get("fast", False)),
                ).outputs,
            }
        if mode == "paper_toolchain":
            return {"graph": graph_trace, **self.paper.plan_toolchain(request, paper_context=kwargs.get("paper_context") or {}).outputs}
        if mode == "prepare_query":
            response = self.agents["ExecutionAgent"].prepare(
                query,
                available_artifacts=request.available_artifacts,
                model_args_by_flow=request.context.get("model_args_by_flow") or {},
            )
            return {"graph": graph_trace, **response.outputs}
        if mode == "prepare_flow_plan":
            return {"graph": graph_trace, **self.execution.prepare_flow_plan(kwargs.get("flow_plan"), request).outputs}
        if mode == "execute_tool":
            return {
                "graph": graph_trace,
                **self.execution.execute_tool(
                    str(kwargs.get("tool_id") or ""),
                    list(kwargs.get("slide_paths") or []),
                    model_args=kwargs.get("model_args"),
                    username=str(kwargs.get("username") or "bioresearch_agent"),
                    extra_slots=kwargs.get("extra_slots"),
                ).outputs,
            }
        if mode == "inspect_manifest":
            return {"graph": graph_trace, **self.readback.inspect_manifest(str(kwargs.get("manifest_path") or "")).outputs}
        if mode == "locate_result_file":
            return {
                "graph": graph_trace,
                **self.readback.locate_result_file(
                    str(kwargs.get("task_id") or ""),
                    str(kwargs.get("filename") or ""),
                    username=str(kwargs.get("username") or "bioresearch_agent"),
                ).outputs,
            }
        if mode == "archive_session":
            return {"graph": graph_trace, **self.archive.archive_session(dict(kwargs.get("session_data") or {})).outputs}
        if mode == "get_session_record":
            response = self.agents["WorkspaceAgent"].get_session_record(
                str(kwargs.get("session_id") or ""),
                user_id=kwargs.get("user_id"),
            )
            return {"graph": graph_trace, **response.outputs}

        raise ValueError(f"unsupported mode: {mode}")

