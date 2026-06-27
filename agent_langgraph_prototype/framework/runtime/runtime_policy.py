"""Runtime policy draft for the isolated prototype."""

RUNTIME_POLICY = {
    "network_default": "deny",
    "execution_default": "deny",
    "requires_approval_for": [
        "ExecutionSkill",
        "tool_execute",
        "flow_execute_real",
        "scheduler_submit",
    ],
    "read_only_skills": [
        "ToolDiscoverySkill",
        "PaperEvidenceSkill",
        "TroubleshootingReadbackSkill",
    ],
}

