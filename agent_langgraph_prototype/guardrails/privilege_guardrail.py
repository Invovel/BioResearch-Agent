"""Prototype privilege guardrail policy."""

RULES = [
    "ExecutionSkill is privileged",
    "tool execute and flow execute real are not available to generic read-only agents",
    "framework decides privilege, skill does not self-authorize",
]

