from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvidenceDoc:
    """Public-safe evidence unit used by retrieval and reports."""

    doc_id: str
    title: str
    source: str
    abstract: str
    tags: tuple[str, ...] = ()
    year: int | None = None
    source_id: str = ""
    url: str = ""
    doi: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ResearchRequest:
    """User request after privacy screening."""

    query: str
    user_role: str = "researcher"
    constraints: tuple[str, ...] = ()
    uploaded_files: tuple[str, ...] = ()
    data_notes: tuple[str, ...] = ()
    allow_tool_execution: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SkillResult:
    """Output returned by a bounded skill."""

    skill_id: str
    summary: str
    bullets: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    review_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ToolResult:
    """Output returned by a registered tool."""

    tool_id: str
    status: str
    output: dict[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReferenceMark:
    """Neutral marker attached to a public reference."""

    doc_id: str
    marker: str
    rationale: str
    polarity: str = "neutral"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReferenceVerification:
    """Evidence check for one neutral marker."""

    doc_id: str
    marker: str
    status: str
    evidence_terms: tuple[str, ...] = ()
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EntityMention:
    """Reviewable public metadata entity mention."""

    entity_type: str
    text: str
    normalized_name: str
    doc_id: str
    evidence_field: str
    confidence: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MemoryWeaverTrace:
    """Public-safe trace of successful and failed workflow paths."""

    run_id: str
    question: str
    query_plan: dict[str, Any]
    success_paths: tuple[dict[str, Any], ...] = ()
    failure_paths: tuple[dict[str, Any], ...] = ()
    evidence_sources: tuple[dict[str, Any], ...] = ()
    path_patterns: tuple[dict[str, Any], ...] = ()
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ManuscriptSectionPlan:
    """Reviewable manuscript section plan."""

    section: str
    purpose: str
    evidence_inputs: tuple[str, ...] = ()
    quality_gate: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ManuscriptWorkflow:
    """Public-safe manuscript workflow inspired by mature academic-writing skill patterns."""

    target_style: str
    strategist_steps: tuple[str, ...]
    composer_steps: tuple[str, ...]
    imrad_outline: tuple[ManuscriptSectionPlan, ...]
    narrative_checks: tuple[str, ...]
    audit_gates: tuple[str, ...]
    reviewer_response_plan: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["imrad_outline"] = [item.to_dict() for item in self.imrad_outline]
        return payload


@dataclass(frozen=True)
class WorkflowContractCheck:
    """Reviewable workflow-stage contract check."""

    stage: str
    status: str
    evidence: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalSkillSpec:
    """Public-safe external SKILL.md descriptor."""

    skill_id: str
    name: str
    description: str
    path: str
    source: str = "local"
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LangGraphNodeSpec:
    """Adapter-neutral node contract for mounting an external skill in LangGraph."""

    node_id: str
    skill_id: str
    trigger_summary: str
    input_contract: tuple[str, ...]
    output_contract: tuple[str, ...]
    safety_policy: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SkillWorkflowSpec:
    """LangGraph-style workflow contract owned by one skill."""

    skill_id: str
    workflow_id: str
    description: str
    nodes: tuple[dict[str, Any], ...]
    edges: tuple[tuple[str, str], ...]
    tool_ids: tuple[str, ...] = ()
    safety_gates: tuple[str, ...] = ()
    memory_policy: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EndToEndReport:
    """Complete public-safe workflow result."""

    question: str
    references: tuple[EvidenceDoc, ...]
    entities: tuple[EntityMention, ...]
    summary: str
    next_workflow: tuple[str, ...]
    manuscript_workflow: ManuscriptWorkflow
    memory_trace: MemoryWeaverTrace
    contract_checks: tuple[WorkflowContractCheck, ...]
    markdown: str
    human_review_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["references"] = [item.to_dict() for item in self.references]
        payload["entities"] = [item.to_dict() for item in self.entities]
        payload["manuscript_workflow"] = self.manuscript_workflow.to_dict()
        payload["memory_trace"] = self.memory_trace.to_dict()
        payload["contract_checks"] = [item.to_dict() for item in self.contract_checks]
        return payload


@dataclass(frozen=True)
class UploadedDataSummary:
    """Public-safe summary of user-uploaded data."""

    data_id: str
    kind: str
    label: str
    observations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DataReliabilityCheck:
    """Reliability check for uploaded data metadata and notes."""

    data_id: str
    status: str
    checks: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PaperDataAlignment:
    """Alignment between one reference and uploaded data observations."""

    doc_id: str
    status: str
    shared_terms: tuple[str, ...] = ()
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InnovationSignal:
    """Potential novelty surfaced from data terms not covered by references."""

    signal: str
    rationale: str
    follow_up_query: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ResearchPlan:
    """Final structured plan produced by the agent."""

    query: str
    intent: str
    evidence: tuple[EvidenceDoc, ...]
    skill_results: tuple[SkillResult, ...]
    tool_results: tuple[ToolResult, ...]
    recommended_steps: tuple[str, ...]
    risks: tuple[str, ...]
    follow_up_questions: tuple[str, ...]
    human_review_required: bool = True
    reference_marks: tuple[ReferenceMark, ...] = ()
    reference_verifications: tuple[ReferenceVerification, ...] = ()
    uploaded_data: tuple[UploadedDataSummary, ...] = ()
    data_reliability: tuple[DataReliabilityCheck, ...] = ()
    paper_data_alignment: tuple[PaperDataAlignment, ...] = ()
    innovation_signals: tuple[InnovationSignal, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence"] = [item.to_dict() for item in self.evidence]
        payload["reference_marks"] = [item.to_dict() for item in self.reference_marks]
        payload["reference_verifications"] = [item.to_dict() for item in self.reference_verifications]
        payload["uploaded_data"] = [item.to_dict() for item in self.uploaded_data]
        payload["data_reliability"] = [item.to_dict() for item in self.data_reliability]
        payload["paper_data_alignment"] = [item.to_dict() for item in self.paper_data_alignment]
        payload["innovation_signals"] = [item.to_dict() for item in self.innovation_signals]
        payload["skill_results"] = [item.to_dict() for item in self.skill_results]
        payload["tool_results"] = [item.to_dict() for item in self.tool_results]
        return payload
