from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .data_workflow import align_papers_to_data, check_data_reliability, find_innovation_signals, summarize_uploads
from .privacy import PrivacyGate
from .reference_workflow import compare_by_marker, mark_references, search_references, verify_marks
from .schemas import EvidenceDoc, ReferenceMark, ToolResult, UploadedDataSummary

ToolHandler = Callable[[dict[str, Any]], ToolResult]


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    description: str
    risk_level: str = "low"
    requires_confirmation: bool = False
    allowed_data: tuple[str, ...] = ("public_text",)
    forbidden_data: tuple[str, ...] = ("patient_data", "private_project_data", "secrets")
    required_inputs: tuple[str, ...] = ()
    produced_outputs: tuple[str, ...] = ()


class ToolRegistry:
    """Registry of public-safe tools."""

    def __init__(self, privacy_gate: PrivacyGate | None = None) -> None:
        self._privacy_gate = privacy_gate or PrivacyGate()
        self._tools: dict[str, tuple[ToolSpec, ToolHandler]] = {}

    def register(self, spec: ToolSpec, handler: ToolHandler) -> None:
        if spec.tool_id in self._tools:
            raise ValueError(f"Duplicate tool_id: {spec.tool_id}")
        self._tools[spec.tool_id] = (spec, handler)

    def run(self, tool_id: str, payload: dict[str, Any], *, confirmed: bool = False) -> ToolResult:
        if tool_id not in self._tools:
            return ToolResult(tool_id=tool_id, status="not_found", warnings=("Unknown tool.",))
        spec, handler = self._tools[tool_id]
        if spec.requires_confirmation and not confirmed:
            return ToolResult(tool_id=tool_id, status="needs_confirmation", warnings=("Confirmation required.",))
        self._privacy_gate.assert_public_safe(str(payload))
        try:
            return handler(payload)
        except Exception:
            return ToolResult(tool_id=tool_id, status="failed", warnings=("Tool handler failed.",))

    def run_chain(
        self,
        tool_ids: tuple[str, ...],
        payload: dict[str, Any],
        *,
        confirmed: bool = False,
    ) -> tuple[ToolResult, ...]:
        """Run tools in order, exposing successful outputs to downstream tools."""

        context = dict(payload)
        results: list[ToolResult] = []
        for tool_id in tool_ids:
            registered = self._tools.get(tool_id)
            if registered is None:
                results.append(self.run(tool_id, context, confirmed=confirmed))
                continue

            spec, _ = registered
            missing_inputs = tuple(key for key in spec.required_inputs if key not in context)
            if missing_inputs:
                results.append(
                    ToolResult(
                        tool_id=tool_id,
                        status="skipped",
                        warnings=(f"Missing required chain inputs: {', '.join(missing_inputs)}.",),
                    )
                )
                continue

            result = self.run(tool_id, context, confirmed=confirmed)
            if result.status == "ok":
                missing_outputs = tuple(key for key in spec.produced_outputs if key not in result.output)
                if missing_outputs:
                    result = ToolResult(
                        tool_id=tool_id,
                        status="failed",
                        output=result.output,
                        warnings=(f"Tool omitted declared outputs: {', '.join(missing_outputs)}.",),
                    )
                else:
                    context.update(result.output)
            results.append(result)
        return tuple(results)

    def list_specs(self) -> tuple[ToolSpec, ...]:
        return tuple(item[0] for item in self._tools.values())

    def get_spec(self, tool_id: str) -> ToolSpec | None:
        item = self._tools.get(tool_id)
        return item[0] if item else None

    @classmethod
    def defaults(cls, privacy_gate: PrivacyGate | None = None) -> "ToolRegistry":
        registry = cls(privacy_gate=privacy_gate)
        registry.register(
            ToolSpec(
                tool_id="public_paper_search",
                description="Search public biomedical-paper metadata placeholder corpus.",
                risk_level="low",
                required_inputs=("query",),
                produced_outputs=("papers",),
            ),
            public_paper_search,
        )
        registry.register(
            ToolSpec(
                tool_id="reference_search",
                description="Search public-safe reference metadata for user-uploaded data questions.",
                risk_level="low",
                required_inputs=("query",),
                produced_outputs=("references",),
            ),
            reference_search,
        )
        registry.register(
            ToolSpec(
                tool_id="data_reliability_check",
                description="Check whether uploaded data metadata and notes are reviewable.",
                risk_level="low",
                produced_outputs=("uploaded_data", "checks"),
            ),
            data_reliability_check,
        )
        registry.register(
            ToolSpec(
                tool_id="paper_data_alignment",
                description="Check whether cited reference metadata aligns with uploaded data observations.",
                risk_level="low",
                required_inputs=("references", "uploaded_data"),
                produced_outputs=("alignments",),
            ),
            paper_data_alignment,
        )
        registry.register(
            ToolSpec(
                tool_id="innovation_scan",
                description="Surface potential novelty from uploaded data terms not covered by current references.",
                risk_level="low",
                required_inputs=("references", "uploaded_data"),
                produced_outputs=("innovation_signals",),
            ),
            innovation_scan,
        )
        registry.register(
            ToolSpec(
                tool_id="reference_mark",
                description="Attach neutral markers to reference metadata.",
                risk_level="low",
                required_inputs=("references",),
                produced_outputs=("marks",),
            ),
            reference_mark,
        )
        registry.register(
            ToolSpec(
                tool_id="marker_verify",
                description="Check whether neutral markers are supported by title/abstract/tags.",
                risk_level="low",
                required_inputs=("references", "marks"),
                produced_outputs=("verifications",),
            ),
            marker_verify,
        )
        registry.register(
            ToolSpec(
                tool_id="marker_compare",
                description="Compare references grouped by the same neutral marker.",
                risk_level="low",
                required_inputs=("references", "marks"),
                produced_outputs=("comparison",),
            ),
            marker_compare,
        )
        registry.register(
            ToolSpec(
                tool_id="markdown_brief_export",
                description="Create a Markdown research brief from structured fields.",
                risk_level="low",
                produced_outputs=("markdown",),
            ),
            markdown_brief_export,
        )
        return registry


def public_paper_search(payload: dict[str, Any]) -> ToolResult:
    query = str(payload.get("query", "")).strip()
    papers = [doc.to_dict() for doc in search_references(query, top_k=int(payload.get("top_k", 3) or 3))]
    return ToolResult(tool_id="public_paper_search", status="ok", output={"papers": papers})


def reference_search(payload: dict[str, Any]) -> ToolResult:
    query = str(payload.get("query", "")).strip()
    top_k = int(payload.get("top_k", 5) or 5)
    refs = search_references(query, top_k=top_k)
    return ToolResult(
        tool_id="reference_search",
        status="ok",
        output={"references": [doc.to_dict() for doc in refs]},
    )


def reference_mark(payload: dict[str, Any]) -> ToolResult:
    refs = _payload_references(payload)
    marks = mark_references(refs)
    return ToolResult(
        tool_id="reference_mark",
        status="ok",
        output={"marks": [mark.to_dict() for mark in marks]},
    )


def data_reliability_check(payload: dict[str, Any]) -> ToolResult:
    data = _payload_uploaded_data(payload)
    if not data:
        data = summarize_uploads(
            tuple(payload.get("uploaded_files", ()) or ()),
            tuple(payload.get("data_notes", ()) or ()),
        )
    checks = check_data_reliability(data)
    return ToolResult(
        tool_id="data_reliability_check",
        status="ok",
        output={
            "uploaded_data": [item.to_dict() for item in data],
            "checks": [check.to_dict() for check in checks],
        },
    )


def paper_data_alignment(payload: dict[str, Any]) -> ToolResult:
    refs = _payload_references(payload)
    data = _payload_uploaded_data(payload)
    alignments = align_papers_to_data(refs, data)
    return ToolResult(
        tool_id="paper_data_alignment",
        status="ok",
        output={"alignments": [item.to_dict() for item in alignments]},
    )


def innovation_scan(payload: dict[str, Any]) -> ToolResult:
    refs = _payload_references(payload)
    data = _payload_uploaded_data(payload)
    signals = find_innovation_signals(refs, data)
    return ToolResult(
        tool_id="innovation_scan",
        status="ok",
        output={"innovation_signals": [item.to_dict() for item in signals]},
    )


def marker_verify(payload: dict[str, Any]) -> ToolResult:
    refs = _payload_references(payload)
    marks = _payload_marks(payload)
    checks = verify_marks(refs, marks)
    return ToolResult(
        tool_id="marker_verify",
        status="ok",
        output={"verifications": [check.to_dict() for check in checks]},
    )


def marker_compare(payload: dict[str, Any]) -> ToolResult:
    refs = _payload_references(payload)
    marks = _payload_marks(payload)
    comparison = compare_by_marker(refs, marks)
    return ToolResult(tool_id="marker_compare", status="ok", output={"comparison": comparison})


def markdown_brief_export(payload: dict[str, Any]) -> ToolResult:
    title = str(payload.get("title", "BioResearch-Agent Brief")).strip()
    bullets = payload.get("bullets", [])
    body = "\n".join(f"- {item}" for item in bullets)
    return ToolResult(tool_id="markdown_brief_export", status="ok", output={"markdown": f"# {title}\n\n{body}\n"})


def _payload_references(payload: dict[str, Any]) -> tuple[EvidenceDoc, ...]:
    refs = payload.get("references", ())
    docs = []
    for item in refs:
        if isinstance(item, EvidenceDoc):
            docs.append(item)
        elif isinstance(item, dict):
            docs.append(
                EvidenceDoc(
                    doc_id=str(item.get("doc_id", "")),
                    title=str(item.get("title", "")),
                    source=str(item.get("source", "")),
                    abstract=str(item.get("abstract", "")),
                    tags=tuple(item.get("tags", ()) or ()),
                    year=item.get("year"),
                )
            )
    return tuple(docs)


def _payload_marks(payload: dict[str, Any]) -> tuple[ReferenceMark, ...]:
    marks = payload.get("marks", ())
    parsed = []
    for item in marks:
        if isinstance(item, ReferenceMark):
            parsed.append(item)
        elif isinstance(item, dict):
            parsed.append(
                ReferenceMark(
                    doc_id=str(item.get("doc_id", "")),
                    marker=str(item.get("marker", "")),
                    rationale=str(item.get("rationale", "")),
                    polarity=str(item.get("polarity", "neutral")),
                )
            )
    return tuple(parsed)


def _payload_uploaded_data(payload: dict[str, Any]) -> tuple[UploadedDataSummary, ...]:
    uploaded = payload.get("uploaded_data", ())
    parsed = []
    for item in uploaded:
        if isinstance(item, UploadedDataSummary):
            parsed.append(item)
        elif isinstance(item, dict):
            parsed.append(
                UploadedDataSummary(
                    data_id=str(item.get("data_id", "")),
                    kind=str(item.get("kind", "")),
                    label=str(item.get("label", "")),
                    observations=tuple(item.get("observations", ()) or ()),
                )
            )
    return tuple(parsed)
