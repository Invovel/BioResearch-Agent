from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .schemas import EvidenceDoc, ResearchRequest, SkillResult

SkillHandler = Callable[[ResearchRequest, tuple[EvidenceDoc, ...]], SkillResult]


@dataclass(frozen=True)
class SkillSpec:
    skill_id: str
    purpose: str
    trigger_terms: tuple[str, ...]
    review_required: bool = True


class SkillRegistry:
    """Registry of bounded reasoning skills."""

    def __init__(self) -> None:
        self._skills: dict[str, tuple[SkillSpec, SkillHandler]] = {}

    def register(self, spec: SkillSpec, handler: SkillHandler) -> None:
        if spec.skill_id in self._skills:
            raise ValueError(f"Duplicate skill_id: {spec.skill_id}")
        self._skills[spec.skill_id] = (spec, handler)

    def select(self, query: str) -> list[tuple[SkillSpec, SkillHandler]]:
        lowered = query.lower()
        selected = [
            item
            for item in self._skills.values()
            if any(term.lower() in lowered for term in item[0].trigger_terms)
        ]
        if selected:
            return selected
        return [self._skills["research_plan"]]

    def list_specs(self) -> tuple[SkillSpec, ...]:
        return tuple(item[0] for item in self._skills.values())

    @classmethod
    def defaults(cls) -> "SkillRegistry":
        registry = cls()
        registry.register(
            SkillSpec(
                skill_id="data_grounded_literature_validation",
                purpose="Use uploaded data observations to search references, validate citation relevance, assess data reliability, and surface novelty.",
                trigger_terms=("paper", "literature", "pubmed", "arxiv", "reference", "citation", "upload", "image", "data", "文献", "论文", "引用", "上传", "图片", "数据"),
            ),
            data_grounded_literature_validation,
        )
        registry.register(
            SkillSpec(
                skill_id="protocol_checklist",
                purpose="Draft a reviewable protocol checklist.",
                trigger_terms=("protocol", "checklist", "experiment", "实验", "方案"),
            ),
            protocol_checklist,
        )
        registry.register(
            SkillSpec(
                skill_id="research_plan",
                purpose="Create a structured biomedical research plan.",
                trigger_terms=("plan", "workflow", "research", "分析", "规划"),
            ),
            research_plan,
        )
        return registry


def data_grounded_literature_validation(request: ResearchRequest, evidence: tuple[EvidenceDoc, ...]) -> SkillResult:
    return SkillResult(
        skill_id="data_grounded_literature_validation",
        summary="Built an uploaded-data grounded literature workflow: cite references, check citation-data alignment, assess data reliability, and surface novelty.",
        bullets=(
            "Uploaded images/data are summarized as public-safe metadata and user observations.",
            "Citation validation checks whether reference metadata aligns with uploaded observations.",
            "Data reliability and novelty are review aids, not clinical conclusions.",
            *(f"{doc.title} ({', '.join(doc.tags)})" for doc in evidence),
        ),
        evidence_ids=tuple(doc.doc_id for doc in evidence),
        review_required=True,
    )


def protocol_checklist(request: ResearchRequest, evidence: tuple[EvidenceDoc, ...]) -> SkillResult:
    return SkillResult(
        skill_id="protocol_checklist",
        summary="Drafted a review checklist for a public-safe biomedical research workflow.",
        bullets=(
            "Define the research question and allowed public inputs.",
            "List evidence sources and exclusion criteria.",
            "Declare tools, expected outputs, and review gates.",
            "Record uncertainties before generating final claims.",
        ),
        evidence_ids=tuple(doc.doc_id for doc in evidence),
        review_required=True,
    )


def research_plan(request: ResearchRequest, evidence: tuple[EvidenceDoc, ...]) -> SkillResult:
    return SkillResult(
        skill_id="research_plan",
        summary="Built a structured research plan from the query, evidence, and available safe tools.",
        bullets=(
            "Clarify goal and biological context.",
            "Retrieve public evidence before selecting tools.",
            "Select bounded tools only after privacy screening.",
            "Export a human-reviewable research brief.",
        ),
        evidence_ids=tuple(doc.doc_id for doc in evidence),
        review_required=True,
    )
