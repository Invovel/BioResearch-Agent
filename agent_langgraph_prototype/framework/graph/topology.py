"""Expanded graph topology draft for the isolated prototype."""

GRAPH = {
    "entry": "role_router",
    "nodes": {
        "role_router": {
            "kind": "framework",
            "responsibility": "Select agent role from query, risk, evidence need, and execution intent.",
            "next": [
                "planner_agent",
                "research_agent",
                "execution_agent",
                "workspace_agent",
            ],
        },
        "planner_agent": {
            "kind": "agent",
            "skills": [
                "ToolDiscoverySkill",
                "QCPreprocessSkill",
                "SegmentationDetectionSkill",
                "NucleusPathomicsSkill",
            ],
        },
        "research_agent": {
            "kind": "agent",
            "skills": [
                "PaperEvidenceSkill",
                "ImmuneTMESkill",
                "MILMultimodalSkill",
                "NucleusPathomicsSkill",
            ],
        },
        "execution_agent": {
            "kind": "agent",
            "skills": [
                "ExecutionSkill",
                "TroubleshootingReadbackSkill",
                "AnnotationPrepSkill",
            ],
            "gates": [
                "privilege_guardrail",
                "execution_guardrail",
                "human_approval",
            ],
        },
        "workspace_agent": {
            "kind": "agent",
            "skills": [
                "ToolDiscoverySkill",
                "PaperEvidenceSkill",
                "TroubleshootingReadbackSkill",
            ],
        },
        "human_approval": {
            "kind": "framework",
            "responsibility": "Pause privileged transitions until approval arrives.",
        },
        "done": {
            "kind": "terminal",
        },
    },
}

