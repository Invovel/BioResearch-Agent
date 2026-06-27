from __future__ import annotations

import re
from pathlib import Path

from .schemas import (
    DataReliabilityCheck,
    EvidenceDoc,
    InnovationSignal,
    PaperDataAlignment,
    UploadedDataSummary,
)


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
TABLE_EXTENSIONS = {".csv", ".tsv"}


def summarize_uploads(uploaded_files: tuple[str, ...], data_notes: tuple[str, ...]) -> tuple[UploadedDataSummary, ...]:
    """Create public-safe summaries for user-uploaded files and notes.

    The current project does not parse image pixels or private data files. It
    records safe metadata and user-provided observations for later review.
    """

    summaries: list[UploadedDataSummary] = []
    observations = tuple(note.strip() for note in data_notes if note.strip())
    for index, filename in enumerate(uploaded_files, start=1):
        label = Path(filename).name
        kind = _kind_from_name(label)
        summaries.append(
            UploadedDataSummary(
                data_id=f"upload-{index}",
                kind=kind,
                label=label,
                observations=observations,
            )
        )
    if not summaries and observations:
        summaries.append(
            UploadedDataSummary(
                data_id="observation-1",
                kind="user_observation",
                label="text_observation",
                observations=observations,
            )
        )
    return tuple(summaries)


def check_data_reliability(data: tuple[UploadedDataSummary, ...]) -> tuple[DataReliabilityCheck, ...]:
    checks: list[DataReliabilityCheck] = []
    for item in data:
        passed: list[str] = []
        warnings: list[str] = []
        if item.kind in {"image", "table", "user_observation"}:
            passed.append("supported_public_demo_type")
        else:
            warnings.append("unknown_file_type")
        if item.observations:
            passed.append("has_user_observations")
        else:
            warnings.append("missing_observation_notes")
        if len(item.label) > 120:
            warnings.append("long_filename_review_needed")
        status = "reviewable" if not warnings else "needs_review"
        checks.append(
            DataReliabilityCheck(
                data_id=item.data_id,
                status=status,
                checks=tuple(passed),
                warnings=tuple(warnings),
            )
        )
    return tuple(checks)


def align_papers_to_data(
    references: tuple[EvidenceDoc, ...],
    data: tuple[UploadedDataSummary, ...],
) -> tuple[PaperDataAlignment, ...]:
    data_terms = _data_terms(data)
    alignments: list[PaperDataAlignment] = []
    for doc in references:
        doc_terms = _tokens(" ".join([doc.title, doc.abstract, " ".join(doc.tags)]))
        shared = tuple(sorted(data_terms & doc_terms))
        status = "supported_by_uploaded_context" if shared else "not_supported_by_uploaded_context"
        note = (
            "Reference metadata overlaps with uploaded-data observations."
            if shared
            else "No direct overlap between reference metadata and uploaded-data observations."
        )
        alignments.append(PaperDataAlignment(doc_id=doc.doc_id, status=status, shared_terms=shared, note=note))
    return tuple(alignments)


def find_innovation_signals(
    references: tuple[EvidenceDoc, ...],
    data: tuple[UploadedDataSummary, ...],
) -> tuple[InnovationSignal, ...]:
    data_terms = _data_terms(data)
    reference_terms: set[str] = set()
    for doc in references:
        reference_terms |= _tokens(" ".join([doc.title, doc.abstract, " ".join(doc.tags)]))
    novel_terms = sorted(term for term in data_terms - reference_terms if len(term) >= 3)[:5]
    return tuple(
        InnovationSignal(
            signal=term,
            rationale="Observed in uploaded-data notes but not covered by current reference metadata.",
            follow_up_query=f"{term} biomedical imaging evidence",
        )
        for term in novel_terms
    )


def _kind_from_name(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in TABLE_EXTENSIONS:
        return "table"
    if not suffix:
        return "user_observation"
    return "unknown"


def _data_terms(data: tuple[UploadedDataSummary, ...]) -> set[str]:
    text = " ".join(
        [
            " ".join(item.observations)
            for item in data
        ]
        + [item.label for item in data]
    )
    return _tokens(text)


def _tokens(text: str) -> set[str]:
    lowered = text.lower()
    latin = set(re.findall(r"[a-z0-9_+-]{2,}", lowered))
    cjk = {char for char in lowered if "\u4e00" <= char <= "\u9fff"}
    return latin | cjk
