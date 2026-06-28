from __future__ import annotations

from dataclasses import dataclass

from .schemas import (
    EntityMention,
    EvidenceDoc,
    ManuscriptWorkflow,
    MemoryWeaverTrace,
    WorkflowContractCheck,
)


@dataclass(frozen=True)
class WorkflowContract:
    """Clean-room workflow contract inspired by mature agent-framework boundaries."""

    stage: str
    required_outputs: tuple[str, ...]
    failure_policy: str
    trace_requirement: str


DEFAULT_WORKFLOW_CONTRACTS: tuple[WorkflowContract, ...] = (
    WorkflowContract(
        stage="privacy_gate",
        required_outputs=("public_safe_question",),
        failure_policy="Block private or clinical-risk inputs before retrieval.",
        trace_requirement="Question must be represented without private data.",
    ),
    WorkflowContract(
        stage="public_retrieval",
        required_outputs=("references", "source_ids"),
        failure_policy="Record empty or failed sources instead of fabricating citations.",
        trace_requirement="Every retained source needs public provenance such as PMID, arXiv ID, DOI, URL, or placeholder source_id.",
    ),
    WorkflowContract(
        stage="entity_extraction",
        required_outputs=("disease_gene_drug_method_dataset_mentions",),
        failure_policy="Record extractor misses as a failure path and keep the summary cautious.",
        trace_requirement="Every entity mention must point to a reference and evidence field.",
    ),
    WorkflowContract(
        stage="research_summary",
        required_outputs=("citation_backed_summary",),
        failure_policy="Use metadata-level wording unless full text or experimental evidence has been verified.",
        trace_requirement="Summary must preserve source mode and cite reference IDs.",
    ),
    WorkflowContract(
        stage="next_workflow",
        required_outputs=("bounded_next_actions",),
        failure_policy="Escalate unsupported claims to human review rather than inventing experiments.",
        trace_requirement="Actions must mention provenance review, expansion, or human approval.",
    ),
    WorkflowContract(
        stage="manuscript_workflow",
        required_outputs=("strategy", "imrad_outline", "audit_gates"),
        failure_policy="Produce scaffold only; never fabricate results, metrics, p-values, or submission claims.",
        trace_requirement="Sections must map to evidence IDs, entities, markers, or pending-review tags.",
    ),
    WorkflowContract(
        stage="memory_trace",
        required_outputs=("success_paths", "failure_paths", "evidence_sources", "warnings"),
        failure_policy="Keep successful and failed paths explicit and public-safe.",
        trace_requirement="Evidence sources must be reusable without exposing private data.",
    ),
)


def build_contract_checks(
    *,
    query: str,
    references: tuple[EvidenceDoc, ...],
    entities: tuple[EntityMention, ...],
    summary: str,
    next_workflow: tuple[str, ...],
    manuscript_workflow: ManuscriptWorkflow,
    trace: MemoryWeaverTrace,
) -> tuple[WorkflowContractCheck, ...]:
    """Validate the current run against clean-room workflow contracts."""

    checks = [
        _check(
            "privacy_gate",
            evidence=(query[:120],) if query else (),
            missing=() if query else ("public_safe_question",),
            note="The PrivacyGate runs before this report object is built.",
        ),
        _check(
            "public_retrieval",
            evidence=tuple(doc.doc_id for doc in references),
            missing=tuple(
                f"{doc.doc_id}:public_provenance"
                for doc in references
                if not (doc.source_id or doc.url or doc.doi or doc.doc_id.startswith(("PMID:", "arXiv:", "bioRxiv:")))
            )
            or (() if references else ("references",)),
            note="References must remain traceable without private files or logs.",
        ),
        _check(
            "entity_extraction",
            evidence=tuple(f"{item.normalized_name}@{item.doc_id}:{item.evidence_field}" for item in entities[:12]),
            missing=() if entities else ("disease_gene_drug_method_dataset_mentions",),
            note="Dictionary extraction is intentionally reviewable and conservative.",
        ),
        _check(
            "research_summary",
            evidence=(summary[:160],) if summary else (),
            missing=() if summary and any(doc.doc_id in summary or doc.source in summary for doc in references) else ("citation_backed_summary",),
            note="Summary is metadata-level triage, not clinical validation.",
        ),
        _check(
            "next_workflow",
            evidence=next_workflow,
            missing=() if next_workflow and any("review" in step.lower() or "approve" in step.lower() for step in next_workflow) else ("bounded_next_actions",),
            note="Next actions must preserve human review and provenance checks.",
        ),
        _check(
            "manuscript_workflow",
            evidence=tuple(item.section for item in manuscript_workflow.imrad_outline),
            missing=(
                *(() if manuscript_workflow.strategist_steps else ("strategy",)),
                *(() if manuscript_workflow.imrad_outline else ("imrad_outline",)),
                *(() if manuscript_workflow.audit_gates else ("audit_gates",)),
            ),
            note="Writing output is a scaffold, not a submission-ready paper.",
        ),
        _check(
            "memory_trace",
            evidence=(
                f"success={len(trace.success_paths)}",
                f"failure={len(trace.failure_paths)}",
                f"evidence={len(trace.evidence_sources)}",
            ),
            missing=(
                *(() if trace.success_paths else ("success_paths",)),
                *(() if trace.evidence_sources else ("evidence_sources",)),
                *(() if trace.warnings else ("warnings",)),
            ),
            note="Failure paths may be empty when all checked stages succeeded.",
        ),
    ]
    return tuple(checks)


def _check(stage: str, *, evidence: tuple[str, ...], missing: tuple[str, ...], note: str) -> WorkflowContractCheck:
    status = "passed" if not missing else "needs_review"
    return WorkflowContractCheck(stage=stage, status=status, evidence=evidence, missing=missing, note=note)
