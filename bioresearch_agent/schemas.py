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
