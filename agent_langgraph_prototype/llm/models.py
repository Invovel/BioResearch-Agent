"""LLM model catalog for skill routing."""

LLM_MODELS = {
    "general_planner_llm": {
        "role": "planning_and_routing",
        "description": "Default planning/model-selection LLM for toolchain and workflow reasoning.",
        "preferred_skills": [
            "ChatPlanningSkill",
            "ToolDiscoverySkill",
            "QCPreprocessSkill",
            "SegmentationDetectionSkill",
            "NucleusPathomicsSkill",
        ],
    },
    "paper_reasoning_llm": {
        "role": "paper_evidence_reasoning",
        "description": "LLM focused on literature summarization, evidence comparison, and paper-to-toolchain mapping.",
        "preferred_skills": [
            "PaperEvidenceSkill",
            "ImmuneTMESkill",
            "MILMultimodalSkill",
        ],
    },
    "execution_control_llm": {
        "role": "execution_preflight_and_control",
        "description": "LLM for execution-stage review, preflight clarification, and guarded execution summaries.",
        "preferred_skills": [
            "ExecutionSkill",
            "TroubleshootingReadbackSkill",
            "AnnotationPrepSkill",
        ],
    },
    "workspace_memory_llm": {
        "role": "workspace_memory_context",
        "description": "LLM for session/project/material memory alignment and archive-oriented context stitching.",
        "preferred_skills": [
            "ArchiveSkill",
            "SessionConversationSkill",
            "ProjectWorkspaceSkill",
            "UploadRecoverySkill",
            "ToolDiscoverySkill",
            "PaperEvidenceSkill",
        ],
    },
    "platform_ops_llm": {
        "role": "platform_ops_and_runtime_governance",
        "description": "LLM for scheduler operations, internal flow harness, auth, and runtime governance.",
        "preferred_skills": [
            "SchedulerOpsSkill",
            "InternalFlowHarnessSkill",
            "AuthIdentitySkill",
        ],
    },
}

