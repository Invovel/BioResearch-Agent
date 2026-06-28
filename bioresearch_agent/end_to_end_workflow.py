from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any

from .live_sources import search_live_references
from .privacy import PrivacyGate
from .reference_workflow import compare_by_marker, mark_references, search_references, verify_marks
from .schemas import (
    EndToEndReport,
    EntityMention,
    EvidenceDoc,
    ManuscriptSectionPlan,
    ManuscriptWorkflow,
    MemoryWeaverTrace,
    ReferenceVerification,
)
from .workflow_contracts import build_contract_checks


ENTITY_TERMS: dict[str, tuple[tuple[str, str], ...]] = {
    "disease": (
        ("breast cancer", "breast cancer"),
        ("tumor microenvironment", "tumor microenvironment"),
        ("tumor", "tumor"),
    ),
    "gene": (
        ("BRCA1", "BRCA1"),
        ("TP53", "TP53"),
        ("EGFR", "EGFR"),
        ("HER2", "HER2"),
    ),
    "drug": (
        ("PARP inhibitor", "PARP inhibitor"),
        ("PARP inhibitors", "PARP inhibitor"),
        ("trastuzumab", "trastuzumab"),
        ("osimertinib", "osimertinib"),
    ),
    "method": (
        ("retrieval augmented generation", "retrieval augmented generation"),
        ("RAG", "retrieval augmented generation"),
        ("entity extraction", "entity extraction"),
        ("spatial transcriptomics", "spatial transcriptomics"),
        ("systematic review", "systematic review"),
        ("workflow", "workflow"),
    ),
    "dataset": (
        ("TCGA", "TCGA"),
        ("GEO", "GEO"),
    ),
}


def run_end_to_end_workflow(
    query: str,
    *,
    top_k: int = 6,
    privacy_gate: PrivacyGate | None = None,
    live_sources: bool = False,
) -> EndToEndReport:
    """Run a complete public-safe report workflow over public metadata."""

    gate = privacy_gate or PrivacyGate()
    gate.assert_public_safe(query)

    source_mode = "live public adapters" if live_sources else "public-safe placeholder adapters"
    references = search_live_references(query, top_k=top_k) if live_sources else search_references(query, top_k=top_k)
    failure_paths: list[dict[str, Any]] = []
    if not references:
        failure_paths.append(
            {
                "stage": "public_retrieval",
                "result": "No direct lexical hits for the original question.",
                "next_action": "Fallback to a broad biomedical evidence workflow query.",
            }
        )
        references = search_references("biomedical evidence workflow citation entity extraction", top_k=top_k)
    if live_sources and any(doc.source.endswith("-live-error") for doc in references):
        failure_paths.append(
            {
                "stage": "live_source_retrieval",
                "result": "At least one live source adapter failed.",
                "next_action": "Inspect adapter warnings and retry with narrower query or later network conditions.",
            }
        )
    if live_sources:
        observed_sources = {doc.source.removesuffix("-live") for doc in references}
        missing_sources = sorted({"pubmed", "arxiv", "biorxiv"} - observed_sources)
        if missing_sources:
            failure_paths.append(
                {
                    "stage": "live_source_coverage",
                    "result": f"No retained references from: {', '.join(missing_sources)}.",
                    "next_action": "Retry with source-specific query terms or increase top_k if broad coverage is required.",
                }
            )

    entities = extract_entities(references)
    marks = mark_references(references)
    verifications = verify_marks(references, marks)
    comparison = compare_by_marker(references, marks)
    summary = build_citation_summary(query, references, entities, verifications, source_mode=source_mode)
    next_workflow = build_next_workflow(entities, comparison, live_sources=live_sources)
    manuscript_workflow = build_manuscript_workflow(query, references, entities, comparison)
    trace = build_memory_trace(
        query=query,
        references=references,
        entities=entities,
        verifications=verifications,
        failure_paths=tuple(failure_paths),
        source_mode=source_mode,
    )
    contract_checks = build_contract_checks(
        query=query,
        references=references,
        entities=entities,
        summary=summary,
        next_workflow=next_workflow,
        manuscript_workflow=manuscript_workflow,
        trace=trace,
    )
    markdown = render_markdown_report(
        query=query,
        references=references,
        entities=entities,
        summary=summary,
        next_workflow=next_workflow,
        manuscript_workflow=manuscript_workflow,
        trace=trace,
        contract_checks=contract_checks,
        verifications=verifications,
        source_mode=source_mode,
    )
    return EndToEndReport(
        question=query,
        references=references,
        entities=entities,
        summary=summary,
        next_workflow=next_workflow,
        manuscript_workflow=manuscript_workflow,
        memory_trace=trace,
        contract_checks=contract_checks,
        markdown=markdown,
        human_review_required=True,
    )


def extract_entities(references: tuple[EvidenceDoc, ...]) -> tuple[EntityMention, ...]:
    """Extract simple disease/gene/drug/method/dataset mentions from public metadata."""

    mentions: list[EntityMention] = []
    seen: set[tuple[str, str, str, str]] = set()
    for doc in references:
        fields = {
            "title": doc.title,
            "abstract": doc.abstract,
            "tag": " ".join(doc.tags),
        }
        for field_name, value in fields.items():
            lowered = value.lower()
            for entity_type, terms in ENTITY_TERMS.items():
                for surface, normalized in terms:
                    if surface.lower() not in lowered:
                        continue
                    key = (entity_type, normalized, doc.doc_id, field_name)
                    if key in seen:
                        continue
                    mentions.append(
                        EntityMention(
                            entity_type=entity_type,
                            text=surface,
                            normalized_name=normalized,
                            doc_id=doc.doc_id,
                            evidence_field=field_name,
                            confidence="high" if field_name in {"title", "tag"} else "medium",
                        )
                    )
                    seen.add(key)
    return tuple(mentions)


def build_citation_summary(
    query: str,
    references: tuple[EvidenceDoc, ...],
    entities: tuple[EntityMention, ...],
    verifications: tuple[ReferenceVerification, ...],
    *,
    source_mode: str = "public-safe placeholder adapters",
) -> str:
    entity_counts = _entity_counts(entities)
    supported = sum(1 for item in verifications if item.status == "supported")
    sources = ", ".join(sorted({doc.source for doc in references})) or "none"
    entity_text = ", ".join(f"{kind}: {count}" for kind, count in sorted(entity_counts.items())) or "no extracted entities"
    return (
        f"For the question '{query}', the {source_mode} run retrieved {len(references)} references "
        f"from {sources}. It extracted {entity_text}. Marker verification found {supported} supported "
        "metadata-level marker checks. These outputs are suitable for research triage and report drafting, "
        "but they are not clinical evidence validation."
    )


def build_next_workflow(
    entities: tuple[EntityMention, ...],
    comparison: dict[str, dict[str, object]],
    *,
    live_sources: bool = False,
) -> tuple[str, ...]:
    entity_terms = sorted({item.normalized_name for item in entities})
    marker_terms = sorted(comparison)
    adapter_step = (
        "Review live PubMed/arXiv/bioRxiv provenance, retry failed source adapters, and save source IDs for human audit."
        if live_sources
        else "Add or replace placeholder adapters with live PubMed/arXiv/bioRxiv adapters before treating the run as a real literature search."
    )
    return (
        "Review the privacy gate result and confirm the question contains only public-safe context.",
        f"Expand searches with extracted entities: {', '.join(entity_terms) if entity_terms else 'no entities extracted; broaden the query'}.",
        f"Group references by neutral markers: {', '.join(marker_terms) if marker_terms else 'no supported markers found'}.",
        "Check each cited claim against visible title, abstract, tags, DOI, PMID, arXiv ID, or bioRxiv ID.",
        adapter_step,
        "Have a human reviewer approve the final summary, gaps, and next experiment or reading plan.",
    )


def build_manuscript_workflow(
    query: str,
    references: tuple[EvidenceDoc, ...],
    entities: tuple[EntityMention, ...],
    comparison: dict[str, dict[str, object]],
) -> ManuscriptWorkflow:
    """Build a manuscript workflow from evidence, learned public skill patterns, and safety gates."""

    entity_terms = sorted({item.normalized_name for item in entities})
    evidence_ids = tuple(doc.doc_id for doc in references[:4])
    marker_terms = tuple(sorted(comparison))
    target_style = "biomedical IMRAD with top-journal narrative discipline"
    return ManuscriptWorkflow(
        target_style=target_style,
        strategist_steps=(
            "Define the target contribution as a testable research claim, not a broad topic.",
            "Select the paper type: evidence map, method note, research protocol, review, or experimental manuscript.",
            "Map every proposed novelty statement to public evidence IDs and explicit gaps.",
            "Choose a target venue family only after checking evidence strength, dataset maturity, and reproducibility readiness.",
            "Freeze an outline only when each section has evidence inputs, limits, and a quality gate.",
        ),
        composer_steps=(
            "Draft from outline to section claims before writing prose.",
            "Write Results and figures before abstract polish, so the story follows the evidence rather than aspiration.",
            "Use restrained top-journal style: concrete nouns, calibrated verbs, and no unsupported performance claims.",
            "Mark unsupported statements as pending instead of inventing citations, results, or methods.",
            "Run a final consistency pass across title, abstract, figures, claims, citations, and limitations.",
        ),
        imrad_outline=(
            ManuscriptSectionPlan(
                section="Title and Abstract",
                purpose="State the biomedical problem, the evidence-backed contribution, and the boundary of the claim.",
                evidence_inputs=evidence_ids,
                quality_gate="Every claim names the object of study and avoids clinical or performance overreach.",
            ),
            ManuscriptSectionPlan(
                section="Introduction",
                purpose="Move from public biomedical need to evidence gap to the specific workflow contribution.",
                evidence_inputs=(*evidence_ids, *marker_terms),
                quality_gate="The gap is backed by retrieved evidence and does not depend on private context.",
            ),
            ManuscriptSectionPlan(
                section="Methods",
                purpose="Describe privacy gate, source adapters, entity extraction, marker verification, MemoryWeaver trace, and report generation.",
                evidence_inputs=("PrivacyGate", "Reference workflow", "MemoryWeaver trace"),
                quality_gate="A reader can reproduce the workflow from public metadata and local commands.",
            ),
            ManuscriptSectionPlan(
                section="Results",
                purpose="Report retrieved sources, extracted entities, marker support, failed paths, and workflow outputs.",
                evidence_inputs=(*evidence_ids, *entity_terms[:6]),
                quality_gate="Results separate observed metadata from interpretation and recommendations.",
            ),
            ManuscriptSectionPlan(
                section="Discussion",
                purpose="Explain what the workflow enables, what it does not prove, and what live adapters or human review must add.",
                evidence_inputs=("failure_paths", "audit_gates", "human_review_required"),
                quality_gate="Limitations are written as boundaries, not excuses.",
            ),
        ),
        narrative_checks=(
            "Does the first paragraph establish why the biomedical question matters without making clinical advice claims?",
            "Does each section have one visible job: motivate, prove, qualify, or operationalize?",
            "Are strong verbs reserved for evidence-backed operations and hedged where evidence is metadata-level only?",
            "Are figures and tables planned before final abstract polish?",
            "Does the final paragraph point to an auditable next workflow rather than a vague future direction?",
        ),
        audit_gates=(
            "Claim-citation gate: every substantive claim links to a reference ID, entity mention, marker verification, or pending-review tag.",
            "Evidence-strength gate: metadata support, full-text support, and experimental validation are not collapsed into one level.",
            "Figure/table gate: each planned display has a single message, source IDs, units when applicable, and caveats.",
            "Reproducibility gate: commands, adapters, extraction rules, and report template are named.",
            "Privacy gate: no patient identifiers, private paths, credentials, private datasets, or internal tool manifests.",
        ),
        reviewer_response_plan=(
            "Create a response table with reviewer point, action taken, changed location, evidence ID, and unresolved risk.",
            "Classify requested changes as evidence, method, framing, figure/table, or wording.",
            "Answer criticism with concrete edits and public evidence rather than defensive prose.",
            "If a requested claim needs private or unavailable evidence, mark it as out of scope or pending human review.",
        ),
    )


def build_memory_trace(
    *,
    query: str,
    references: tuple[EvidenceDoc, ...],
    entities: tuple[EntityMention, ...],
    verifications: tuple[ReferenceVerification, ...],
    failure_paths: tuple[dict[str, Any], ...],
    source_mode: str,
) -> MemoryWeaverTrace:
    run_id = _run_id(query, references)
    entity_counts = _entity_counts(entities)
    source_names = sorted({doc.source for doc in references})
    live = source_mode.startswith("live")
    success_paths = (
        {
            "stage": "public_retrieval",
            "result": f"Retrieved {len(references)} public metadata records.",
            "evidence_ids": [doc.doc_id for doc in references],
        },
        {
            "stage": "entity_extraction",
            "result": f"Extracted {sum(entity_counts.values())} entity mentions.",
            "entity_counts": entity_counts,
        },
        {
            "stage": "marker_verification",
            "result": f"Checked {len(verifications)} neutral marker assignments.",
            "supported": sum(1 for item in verifications if item.status == "supported"),
        },
    )
    if not entities:
        failure_paths = (
            *failure_paths,
            {
                "stage": "entity_extraction",
                "result": "No disease/gene/drug/method/dataset entities found in visible metadata.",
                "next_action": "Broaden query or add public ontology-backed extraction.",
            },
        )
    evidence_sources = tuple(
        {
            "reference_id": doc.doc_id,
            "source": doc.source,
            "title": doc.title,
            "year": doc.year,
            "url": doc.url,
            "doi": doc.doi,
            "source_id": doc.source_id,
        }
        for doc in references
    )
    path_patterns = (
        {
            "condition": "A public-safe biomedical research question needs literature triage and writing workflow scaffolding.",
            "action_policy": "Run privacy gate, public retrieval, entity extraction, marker verification, citation summary, next workflow, manuscript scaffold, and contract checks.",
            "validation_gate": "References must have public provenance; entities must cite evidence fields; contracts and tests must pass.",
            "fallback": "If live retrieval is sparse or a source fails, record failure path and retry with source-specific terms or placeholder mode for deterministic tests.",
            "rollback_rule": "Do not promote a path when expected entities are missing, contract checks fail, source provenance is absent, or human review rejects the output.",
            "status": "provisional",
            "evidence_ids": [doc.doc_id for doc in references],
        },
    )
    return MemoryWeaverTrace(
        run_id=run_id,
        question=query,
        query_plan={
            "sources": source_names,
            "top_k": len(references),
            "mode": source_mode,
        },
        success_paths=success_paths,
        failure_paths=failure_paths,
        evidence_sources=evidence_sources,
        path_patterns=path_patterns,
        warnings=(
            "This run uses live public metadata adapters." if live else "This run uses local placeholder public metadata, not live PubMed/arXiv/bioRxiv APIs.",
            "Manuscript workflow is a strategy and QA scaffold, not a generated submission-ready paper.",
            "Human review is required for biomedical claims.",
        ),
    )


def render_markdown_report(
    *,
    query: str,
    references: tuple[EvidenceDoc, ...],
    entities: tuple[EntityMention, ...],
    summary: str,
    next_workflow: tuple[str, ...],
    manuscript_workflow: ManuscriptWorkflow,
    trace: MemoryWeaverTrace,
    contract_checks: tuple[WorkflowContractCheck, ...],
    verifications: tuple[ReferenceVerification, ...],
    source_mode: str,
) -> str:
    lines = [
        "# BioResearch-Agent End-to-End Report",
        "",
        "## Research Question",
        "",
        query,
        "",
        "## Search Scope And Sources",
        "",
        f"- Mode: {source_mode}",
        "- Target sources: PubMed / arXiv / bioRxiv",
        f"- Retrieved references: {len(references)}",
        "",
        "## Citation-Backed Research Summary",
        "",
        summary,
        "",
        "## Key Evidence",
        "",
    ]
    for doc in references:
        year = f", {doc.year}" if doc.year else ""
        url = f" {doc.url}" if doc.url else ""
        doi = f" DOI: {doc.doi}." if doc.doi else ""
        lines.append(f"- [{doc.doc_id}] {doc.title} ({doc.source}{year}).{doi}{url}")
    lines.extend(["", "## Extracted Entities", "", "| Type | Entity | Evidence Field | Reference |", "| --- | --- | --- | --- |"])
    for item in entities:
        lines.append(f"| {item.entity_type} | {item.normalized_name} | {item.evidence_field} | {item.doc_id} |")
    if not entities:
        lines.append("| none | none | none | none |")
    lines.extend(["", "## Marker Verification", "", "| Marker | Status | Evidence Terms | Reference |", "| --- | --- | --- | --- |"])
    for item in verifications:
        terms = ", ".join(item.evidence_terms) if item.evidence_terms else "none"
        lines.append(f"| {item.marker} | {item.status} | {terms} | {item.doc_id} |")
    if not verifications:
        lines.append("| none | none | none | none |")
    lines.extend(["", "## Next-Step Workflow", ""])
    for index, step in enumerate(next_workflow, start=1):
        lines.append(f"{index}. {step}")
    lines.extend(
        [
            "",
            "## Manuscript Workflow Package",
            "",
            f"- Target style: {manuscript_workflow.target_style}",
            "- Learned pattern basis: skill pack layering, strategist/composer split, IMRAD section contracts, top-journal narrative restraint, and paper-audit quality gates.",
            "",
            "### Strategist Steps",
            "",
        ]
    )
    for index, step in enumerate(manuscript_workflow.strategist_steps, start=1):
        lines.append(f"{index}. {step}")
    lines.extend(["", "### Composer Steps", ""])
    for index, step in enumerate(manuscript_workflow.composer_steps, start=1):
        lines.append(f"{index}. {step}")
    lines.extend(["", "### IMRAD Outline", "", "| Section | Purpose | Evidence Inputs | Quality Gate |", "| --- | --- | --- | --- |"])
    for item in manuscript_workflow.imrad_outline:
        evidence = ", ".join(item.evidence_inputs) if item.evidence_inputs else "pending"
        lines.append(f"| {item.section} | {item.purpose} | {evidence} | {item.quality_gate} |")
    lines.extend(["", "### Narrative Checks", ""])
    for item in manuscript_workflow.narrative_checks:
        lines.append(f"- {item}")
    lines.extend(["", "### Audit Gates", ""])
    for item in manuscript_workflow.audit_gates:
        lines.append(f"- {item}")
    lines.extend(["", "### Reviewer Response Plan", ""])
    for index, step in enumerate(manuscript_workflow.reviewer_response_plan, start=1):
        lines.append(f"{index}. {step}")
    lines.extend(
        [
            "",
            "## MemoryWeaver Trace Summary",
            "",
            f"- Run ID: `{trace.run_id}`",
            f"- Success paths: {len(trace.success_paths)}",
            f"- Failure paths: {len(trace.failure_paths)}",
            f"- Evidence sources: {len(trace.evidence_sources)}",
            f"- Weaver-compatible path patterns: {len(trace.path_patterns)}",
            "",
            "## Framework Contract Checks",
            "",
            "| Stage | Status | Missing |",
            "| --- | --- | --- |",
        ]
    )
    for item in contract_checks:
        missing = ", ".join(item.missing) if item.missing else "none"
        lines.append(f"| {item.stage} | {item.status} | {missing} |")
    lines.extend(["", "## Weaver-Compatible Path Patterns", ""])
    for item in trace.path_patterns:
        lines.extend(
            [
                f"- Condition: {item.get('condition', '')}",
                f"  - Action policy: {item.get('action_policy', '')}",
                f"  - Validation gate: {item.get('validation_gate', '')}",
                f"  - Fallback: {item.get('fallback', '')}",
                f"  - Rollback rule: {item.get('rollback_rule', '')}",
            ]
        )
    lines.extend(
        [
            "",
            "## Caveats",
            "",
        ]
    )
    for warning in trace.warnings:
        lines.append(f"- {warning}")
    return "\n".join(lines) + "\n"


def _entity_counts(entities: tuple[EntityMention, ...]) -> dict[str, int]:
    counts: dict[str, set[str]] = defaultdict(set)
    for item in entities:
        counts[item.entity_type].add(item.normalized_name)
    return {key: len(value) for key, value in counts.items()}


def _run_id(query: str, references: tuple[EvidenceDoc, ...]) -> str:
    seed = "|".join([query, *(doc.doc_id for doc in references)])
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
