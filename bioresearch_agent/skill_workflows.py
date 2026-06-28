from __future__ import annotations

from .schemas import LangGraphNodeSpec, SkillWorkflowSpec


DATA_GROUNDED_TOOL_CHAIN = (
    "reference_search",
    "data_reliability_check",
    "paper_data_alignment",
    "innovation_scan",
    "reference_mark",
    "marker_verify",
    "marker_compare",
)

PROTOCOL_TOOL_CHAIN = (
    "public_paper_search",
    "markdown_brief_export",
)

RESEARCH_PLAN_TOOL_CHAIN = (
    "public_paper_search",
    "markdown_brief_export",
)


def default_skill_workflows() -> tuple[SkillWorkflowSpec, ...]:
    """Internal skills as LangGraph-style workflow + tool bundles."""

    return (
        SkillWorkflowSpec(
            skill_id="data_grounded_literature_validation",
            workflow_id="workflow.data_grounded_literature_validation.v1",
            description="Validate public literature against uploaded-data observations with citation, marker, and novelty checks.",
            nodes=(
                _gate("privacy_gate", "Block private data before retrieval."),
                _tool("reference_search", "Search public references."),
                _tool("data_reliability_check", "Check uploaded-data metadata reliability."),
                _tool("paper_data_alignment", "Align reference metadata to uploaded observations."),
                _tool("innovation_scan", "Find uploaded-data terms not covered by references."),
                _tool("reference_mark", "Attach neutral reference markers."),
                _tool("marker_verify", "Verify marker support in visible metadata."),
                _tool("marker_compare", "Compare same-marker references."),
                _skill("skill_summary", "Produce reviewable literature-validation summary."),
                _memory("memory_trace", "Record success, failure, evidence, and Weaver path pattern."),
            ),
            edges=(
                ("privacy_gate", "reference_search"),
                ("reference_search", "data_reliability_check"),
                ("data_reliability_check", "paper_data_alignment"),
                ("paper_data_alignment", "innovation_scan"),
                ("innovation_scan", "reference_mark"),
                ("reference_mark", "marker_verify"),
                ("marker_verify", "marker_compare"),
                ("marker_compare", "skill_summary"),
                ("skill_summary", "memory_trace"),
            ),
            tool_ids=DATA_GROUNDED_TOOL_CHAIN,
            safety_gates=("privacy_gate", "human_review_required", "metadata_is_not_clinical_validation"),
            memory_policy="Promote only if references are traceable, marker verification runs, and human review does not reject the route.",
        ),
        SkillWorkflowSpec(
            skill_id="protocol_checklist",
            workflow_id="workflow.protocol_checklist.v1",
            description="Create a public-safe protocol checklist from the research question and candidate references.",
            nodes=(
                _gate("privacy_gate", "Block private or clinical-decision inputs."),
                _tool("public_paper_search", "Retrieve candidate public evidence."),
                _skill("protocol_checklist", "Draft protocol checklist scaffold."),
                _tool("markdown_brief_export", "Export reviewable Markdown brief."),
                _memory("memory_trace", "Record checklist route and missing evidence."),
            ),
            edges=(
                ("privacy_gate", "public_paper_search"),
                ("public_paper_search", "protocol_checklist"),
                ("protocol_checklist", "markdown_brief_export"),
                ("markdown_brief_export", "memory_trace"),
            ),
            tool_ids=PROTOCOL_TOOL_CHAIN,
            safety_gates=("privacy_gate", "no_fabricated_protocol_claims", "human_review_required"),
            memory_policy="Promote only if protocol items are evidence-bounded and unsupported items are marked for review.",
        ),
        SkillWorkflowSpec(
            skill_id="research_plan",
            workflow_id="workflow.research_plan.v1",
            description="Plan a public-safe biomedical research workflow from query, evidence, tools, and review gates.",
            nodes=(
                _gate("privacy_gate", "Block unsafe inputs."),
                _tool("public_paper_search", "Retrieve lightweight public evidence."),
                _skill("research_plan", "Create bounded workflow plan."),
                _tool("markdown_brief_export", "Export reviewable Markdown brief."),
                _memory("memory_trace", "Record selected route and fallback."),
            ),
            edges=(
                ("privacy_gate", "public_paper_search"),
                ("public_paper_search", "research_plan"),
                ("research_plan", "markdown_brief_export"),
                ("markdown_brief_export", "memory_trace"),
            ),
            tool_ids=RESEARCH_PLAN_TOOL_CHAIN,
            safety_gates=("privacy_gate", "public_evidence_only", "human_review_required"),
            memory_policy="Promote only if the plan preserves public-safe scope and names required review gates.",
        ),
    )


def workflow_for_skill(skill_id: str) -> SkillWorkflowSpec | None:
    return {item.skill_id: item for item in default_skill_workflows()}.get(skill_id)


def workflow_langgraph_nodes(workflow: SkillWorkflowSpec) -> tuple[LangGraphNodeSpec, ...]:
    """Expose an internal workflow as adapter-neutral LangGraph node specs."""

    nodes = []
    for node in workflow.nodes:
        node_id = str(node["node_id"])
        nodes.append(
            LangGraphNodeSpec(
                node_id=f"{workflow.workflow_id}::{node_id}",
                skill_id=workflow.skill_id,
                trigger_summary=str(node.get("description", "")),
                input_contract=("graph_state", "public_safe_context"),
                output_contract=(f"{node_id}_result", "updated_graph_state"),
                safety_policy=workflow.safety_gates,
            )
        )
    return tuple(nodes)


def _gate(node_id: str, description: str) -> dict[str, str]:
    return {"node_id": node_id, "kind": "gate", "description": description}


def _tool(node_id: str, description: str) -> dict[str, str]:
    return {"node_id": node_id, "kind": "tool", "description": description, "tool_id": node_id}


def _skill(node_id: str, description: str) -> dict[str, str]:
    return {"node_id": node_id, "kind": "skill", "description": description}


def _memory(node_id: str, description: str) -> dict[str, str]:
    return {"node_id": node_id, "kind": "memory", "description": description}
