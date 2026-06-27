from __future__ import annotations

from collections import defaultdict

from .retrieval import SimpleRetriever
from .schemas import EvidenceDoc, ReferenceMark, ReferenceVerification


MARKER_TERMS: dict[str, tuple[str, ...]] = {
    "agent-workflow": ("agent", "workflow", "planner", "planning"),
    "rag-evidence": ("rag", "retrieval", "evidence", "citation"),
    "privacy-review": ("privacy", "review", "safety", "boundary"),
    "tool-orchestration": ("tool", "adapter", "execution", "orchestration"),
}


def search_references(query: str, *, top_k: int = 5, retriever: SimpleRetriever | None = None) -> tuple[EvidenceDoc, ...]:
    """Search public-safe reference metadata."""

    active_retriever = retriever or SimpleRetriever()
    return tuple(hit.doc for hit in active_retriever.search(query, top_k=top_k) if hit.score > 0)


def mark_references(references: tuple[EvidenceDoc, ...]) -> tuple[ReferenceMark, ...]:
    """Attach neutral markers to references without judging quality."""

    marks: list[ReferenceMark] = []
    for doc in references:
        haystack = _doc_text(doc)
        for marker, terms in MARKER_TERMS.items():
            matched = tuple(term for term in terms if term in haystack)
            if matched:
                marks.append(
                    ReferenceMark(
                        doc_id=doc.doc_id,
                        marker=marker,
                        rationale=f"Matched neutral terms: {', '.join(matched)}",
                    )
                )
    return tuple(marks)


def verify_marks(
    references: tuple[EvidenceDoc, ...],
    marks: tuple[ReferenceMark, ...],
) -> tuple[ReferenceVerification, ...]:
    """Check whether each marker is supported by reference metadata."""

    docs = {doc.doc_id: doc for doc in references}
    checks: list[ReferenceVerification] = []
    for mark in marks:
        doc = docs.get(mark.doc_id)
        if doc is None:
            checks.append(
                ReferenceVerification(
                    doc_id=mark.doc_id,
                    marker=mark.marker,
                    status="needs_review",
                    note="Reference metadata is missing.",
                )
            )
            continue
        haystack = _doc_text(doc)
        terms = MARKER_TERMS.get(mark.marker, ())
        evidence_terms = tuple(term for term in terms if term in haystack)
        status = "supported" if evidence_terms else "needs_review"
        note = "Marker is supported by title/abstract/tags." if evidence_terms else "No direct metadata support found."
        checks.append(
            ReferenceVerification(
                doc_id=doc.doc_id,
                marker=mark.marker,
                status=status,
                evidence_terms=evidence_terms,
                note=note,
            )
        )
    return tuple(checks)


def compare_by_marker(
    references: tuple[EvidenceDoc, ...],
    marks: tuple[ReferenceMark, ...],
) -> dict[str, dict[str, object]]:
    """Group references sharing the same marker for comparison and expansion."""

    docs = {doc.doc_id: doc for doc in references}
    grouped: dict[str, list[EvidenceDoc]] = defaultdict(list)
    for mark in marks:
        doc = docs.get(mark.doc_id)
        if doc and doc not in grouped[mark.marker]:
            grouped[mark.marker].append(doc)

    comparison: dict[str, dict[str, object]] = {}
    for marker, docs_for_marker in sorted(grouped.items()):
        tag_sets = [set(doc.tags) for doc in docs_for_marker]
        shared_tags = set.intersection(*tag_sets) if tag_sets else set()
        all_tags = set.union(*tag_sets) if tag_sets else set()
        comparison[marker] = {
            "doc_ids": [doc.doc_id for doc in docs_for_marker],
            "shared_tags": sorted(shared_tags),
            "distinct_tags": sorted(all_tags - shared_tags),
            "expansion_queries": [
                f"{marker} benchmark",
                f"{marker} comparison",
                f"{marker} reproducibility",
            ],
        }
    return comparison


def _doc_text(doc: EvidenceDoc) -> str:
    return " ".join([doc.title, doc.abstract, " ".join(doc.tags)]).lower()
