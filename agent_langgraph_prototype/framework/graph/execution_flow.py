"""Execution-path subgraph sketch."""

EXECUTION_SUBGRAPH = {
    "entry": "execution_intent_check",
    "nodes": {
        "execution_intent_check": {
            "responsibility": "Confirm request is execution-oriented rather than planning-only.",
            "next": ["preflight_check", "done"],
        },
        "preflight_check": {
            "responsibility": "Validate artifacts, parameters, and model readiness.",
            "next": ["approval_gate", "done"],
        },
        "approval_gate": {
            "responsibility": "Require explicit approval before privileged execution.",
            "next": ["dispatch_execution", "done"],
        },
        "dispatch_execution": {
            "responsibility": "Send execution request through approved adapter path.",
            "next": ["readback_review", "done"],
        },
        "readback_review": {
            "responsibility": "Summarize outputs, manifests, previews, and failure diagnostics.",
            "next": ["done"],
        },
        "done": {},
    },
}

