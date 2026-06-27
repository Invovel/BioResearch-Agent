"""Prototype agent roles mapped to BioResearch-Agent skills."""

try:
    from agent_langgraph_prototype.agents.execution_agent import ExecutionAgent
    from agent_langgraph_prototype.agents.planner_agent import PlannerAgent
    from agent_langgraph_prototype.agents.research_agent import ResearchAgent
    from agent_langgraph_prototype.agents.workspace_agent import WorkspaceAgent
except ModuleNotFoundError:
    from agent_langgraph_prototype.agents.execution_agent import ExecutionAgent
    from agent_langgraph_prototype.agents.planner_agent import PlannerAgent
    from agent_langgraph_prototype.agents.research_agent import ResearchAgent
    from agent_langgraph_prototype.agents.workspace_agent import WorkspaceAgent


AGENT_ROLES = {
    "PlannerAgent": {
        "skills": [
            "ToolDiscoverySkill",
            "QCPreprocessSkill",
            "SegmentationDetectionSkill",
            "NucleusPathomicsSkill",
        ],
        "notes": "Default planning agent for task recommendation and workflow composition.",
    },
    "ResearchAgent": {
        "skills": [
            "PaperEvidenceSkill",
            "ImmuneTMESkill",
            "MILMultimodalSkill",
            "NucleusPathomicsSkill",
        ],
        "notes": "Evidence-backed recommendation and paper-grounded workflow analysis.",
    },
    "ExecutionAgent": {
        "skills": [
            "ExecutionSkill",
            "TroubleshootingReadbackSkill",
            "AnnotationPrepSkill",
        ],
        "notes": "Privileged execution pathway with readback and failure diagnosis.",
    },
    "WorkspaceAgent": {
        "skills": [
            "PaperEvidenceSkill",
            "ToolDiscoverySkill",
            "TroubleshootingReadbackSkill",
        ],
        "notes": "Session, materials, and evidence-context helper agent.",
    },
}


def build_agent_instances() -> dict:
    return {
        "PlannerAgent": PlannerAgent(),
        "ResearchAgent": ResearchAgent(),
        "ExecutionAgent": ExecutionAgent(),
        "WorkspaceAgent": WorkspaceAgent(),
    }

