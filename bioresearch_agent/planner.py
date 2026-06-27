from __future__ import annotations

from .data_workflow import align_papers_to_data, check_data_reliability, find_innovation_signals, summarize_uploads
from .privacy import PrivacyGate
from .reference_workflow import mark_references, verify_marks
from .retrieval import SimpleRetriever
from .schemas import EvidenceDoc, ResearchPlan, ResearchRequest, ToolResult
from .skills import SkillRegistry
from .tools import ToolRegistry


class BioResearchAgent:
    """Small public-safe biomedical research agent."""

    def __init__(
        self,
        *,
        retriever: SimpleRetriever | None = None,
        skills: SkillRegistry | None = None,
        tools: ToolRegistry | None = None,
        privacy_gate: PrivacyGate | None = None,
    ) -> None:
        self.privacy_gate = privacy_gate or PrivacyGate()
        self.retriever = retriever or SimpleRetriever()
        self.skills = skills or SkillRegistry.defaults()
        self.tools = tools or ToolRegistry.defaults(privacy_gate=self.privacy_gate)

    def plan(self, request: ResearchRequest) -> ResearchPlan:
        self.privacy_gate.assert_public_safe(request.query)
        for item in (*request.uploaded_files, *request.data_notes):
            self.privacy_gate.assert_public_safe(item)
        intent = classify_intent(request.query)
        evidence = tuple(hit.doc for hit in self.retriever.search(request.query, top_k=3) if hit.score > 0)
        if not evidence:
            evidence = tuple(hit.doc for hit in self.retriever.search("biomedical evidence privacy workflow", top_k=2))

        uploaded_data = summarize_uploads(request.uploaded_files, request.data_notes)
        data_reliability = check_data_reliability(uploaded_data)
        paper_data_alignment = align_papers_to_data(evidence, uploaded_data)
        innovation_signals = find_innovation_signals(evidence, uploaded_data)
        reference_marks = mark_references(evidence)
        reference_verifications = verify_marks(evidence, reference_marks)
        skill_results = tuple(handler(request, evidence) for _, handler in self.skills.select(request.query))
        tool_results: tuple[ToolResult, ...] = ()
        if request.allow_tool_execution:
            tool_results = self.tools.run_chain(
                (
                    "reference_search",
                    "data_reliability_check",
                    "paper_data_alignment",
                    "innovation_scan",
                    "reference_mark",
                    "marker_verify",
                    "marker_compare",
                ),
                {
                    "query": request.query,
                    "top_k": 5,
                    "uploaded_files": request.uploaded_files,
                    "data_notes": request.data_notes,
                },
            )

        recommended_steps = (
            "Screen the query with the privacy gate.",
            "Summarize uploaded images/data as public-safe metadata and observations.",
            "Check whether uploaded data is reliable enough for review.",
            "Search related references and cite them as evidence candidates.",
            "Verify whether cited reference metadata aligns with uploaded observations.",
            "Surface potential innovation signals from uploaded data terms not covered by current references.",
        )
        risks = (
            "Do not use private datasets or institution-specific workflow details in public demos.",
            "Do not present generated biomedical text as clinical advice.",
            "Do not treat metadata alignment as proof that a full paper is correct.",
            "Do not infer image content beyond user-provided observations until a public image adapter is added.",
        )
        follow_up_questions = (
            "What visible features should be extracted from the uploaded image or data?",
            "Which references should be treated as citation candidates?",
            "What standard should the human reviewer use for reliability and novelty?",
        )
        return ResearchPlan(
            query=request.query,
            intent=intent,
            evidence=evidence,
            skill_results=skill_results,
            tool_results=tool_results,
            recommended_steps=recommended_steps,
            risks=risks,
            follow_up_questions=follow_up_questions,
            human_review_required=True,
            reference_marks=reference_marks,
            reference_verifications=reference_verifications,
            uploaded_data=uploaded_data,
            data_reliability=data_reliability,
            paper_data_alignment=paper_data_alignment,
            innovation_signals=innovation_signals,
        )


def classify_intent(query: str) -> str:
    lowered = query.lower()
    data_terms = ("upload", "image", "figure", "data", "图片", "图像", "上传", "数据")
    literature_terms = ("paper", "literature", "pubmed", "arxiv", "reference", "citation", "文献", "论文", "引用")
    protocol_terms = ("protocol", "checklist", "experiment", "实验", "方案")
    tool_terms = ("tool", "execute", "run", "工具", "运行", "执行")
    if any(term in lowered for term in literature_terms):
        return "data_grounded_literature_validation"
    if any(term in lowered for term in literature_terms):
        return "data_grounded_literature_validation"
    if any(term in lowered for term in protocol_terms):
        return "protocol_planning"
    if any(term in lowered for term in tool_terms):
        return "tool_aware_planning"
    return "research_planning"
