from __future__ import annotations

import re
from dataclasses import dataclass

from .schemas import EvidenceDoc


DEFAULT_PUBLIC_CORPUS: tuple[EvidenceDoc, ...] = (
    EvidenceDoc(
        doc_id="pubmed-brca1-breast-cancer",
        title="BRCA1-associated breast cancer evidence mapping",
        source="pubmed-placeholder",
        abstract="A public biomedical review can connect breast cancer, BRCA1, PARP inhibitors, and systematic review methods for citation-backed research planning.",
        tags=("disease:breast cancer", "gene:BRCA1", "drug:PARP inhibitor", "method:systematic review"),
        year=2025,
        source_id="placeholder:pubmed-brca1-breast-cancer",
    ),
    EvidenceDoc(
        doc_id="biorxiv-spatial-tme-dataset",
        title="Spatial transcriptomics datasets for tumor microenvironment analysis",
        source="biorxiv-placeholder",
        abstract="Preprint metadata describes spatial transcriptomics methods, tumor microenvironment profiling, and public datasets such as TCGA and GEO for exploratory biomedical workflows.",
        tags=("method:spatial transcriptomics", "dataset:TCGA", "dataset:GEO", "disease:tumor"),
        year=2026,
        source_id="placeholder:biorxiv-spatial-tme-dataset",
    ),
    EvidenceDoc(
        doc_id="arxiv-biomedical-rag-method",
        title="Retrieval augmented generation methods for biomedical literature agents",
        source="arxiv-placeholder",
        abstract="Biomedical RAG methods use retrieval, citations, entity extraction, and workflow traces to separate evidence from generated summaries.",
        tags=("method:RAG", "method:entity extraction", "agent", "citation"),
        year=2025,
        source_id="placeholder:arxiv-biomedical-rag-method",
    ),
    EvidenceDoc(
        doc_id="pubmed-review-agent-workflows",
        title="Agent-assisted biomedical workflow planning",
        source="public-literature-placeholder",
        abstract="Biomedical research assistants can decompose questions, retrieve evidence, and draft reviewable analysis plans.",
        tags=("agent", "workflow", "planning"),
        year=2025,
        source_id="placeholder:pubmed-review-agent-workflows",
    ),
    EvidenceDoc(
        doc_id="public-rag-evidence",
        title="Evidence retrieval for biomedical question answering",
        source="public-literature-placeholder",
        abstract="Retrieval augmented systems should separate retrieved evidence from generated reasoning and final claims.",
        tags=("rag", "evidence", "citation"),
        year=2024,
        source_id="placeholder:public-rag-evidence",
    ),
    EvidenceDoc(
        doc_id="tool-orchestration-boundary",
        title="Tool orchestration boundaries for biomedical research agents",
        source="public-literature-placeholder",
        abstract="Safe research agents use tool adapters, execution gates, and reviewable action plans before running external tools.",
        tags=("tool", "adapter", "execution", "review"),
        year=2025,
        source_id="placeholder:tool-orchestration-boundary",
    ),
    EvidenceDoc(
        doc_id="reference-marker-comparison",
        title="Neutral reference markers for literature comparison",
        source="public-literature-placeholder",
        abstract="Reference markers can group papers for comparison and expansion without ranking them as good or bad.",
        tags=("marker", "comparison", "evidence"),
        year=2026,
        source_id="placeholder:reference-marker-comparison",
    ),
    EvidenceDoc(
        doc_id="privacy-review-boundary",
        title="Privacy-aware biomedical AI assistance",
        source="public-literature-placeholder",
        abstract="Biomedical AI systems require privacy screening, human review, and clear boundaries for high-risk claims.",
        tags=("privacy", "review", "safety"),
        year=2024,
        source_id="placeholder:privacy-review-boundary",
    ),
)


@dataclass(frozen=True)
class RetrievalHit:
    doc: EvidenceDoc
    score: float


class SimpleRetriever:
    """Dependency-free lexical retriever for public-safe demos."""

    def __init__(self, corpus: tuple[EvidenceDoc, ...] = DEFAULT_PUBLIC_CORPUS):
        self._corpus = corpus

    def search(self, query: str, *, top_k: int = 3) -> list[RetrievalHit]:
        query_terms = _tokens(query)
        hits: list[RetrievalHit] = []
        for doc in self._corpus:
            text = " ".join([doc.title, doc.abstract, " ".join(doc.tags)])
            doc_terms = _tokens(text)
            overlap = len(query_terms & doc_terms)
            if overlap == 0:
                score = 0.0
            else:
                score = overlap / max(len(query_terms), 1)
            hits.append(RetrievalHit(doc=doc, score=round(score, 4)))
        hits.sort(key=lambda item: item.score, reverse=True)
        return hits[:top_k]


def _tokens(text: str) -> set[str]:
    lowered = text.lower()
    latin = set(re.findall(r"[a-z0-9_+-]{2,}", lowered))
    cjk = {char for char in lowered if "\u4e00" <= char <= "\u9fff"}
    return latin | cjk
