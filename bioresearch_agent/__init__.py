"""BioResearch-Agent public-safe research assistant scaffold."""

from .planner import BioResearchAgent
from .schemas import (
    EndToEndReport,
    EntityMention,
    EvidenceDoc,
    ManuscriptSectionPlan,
    ManuscriptWorkflow,
    MemoryWeaverTrace,
    ResearchPlan,
    ResearchRequest,
    SkillResult,
    SkillWorkflowSpec,
    ToolResult,
    WorkflowContractCheck,
)

__all__ = [
    "BioResearchAgent",
    "EndToEndReport",
    "EntityMention",
    "EvidenceDoc",
    "ManuscriptSectionPlan",
    "ManuscriptWorkflow",
    "MemoryWeaverTrace",
    "ResearchPlan",
    "ResearchRequest",
    "SkillResult",
    "SkillWorkflowSpec",
    "ToolResult",
    "WorkflowContractCheck",
]

__version__ = "0.1.0"
