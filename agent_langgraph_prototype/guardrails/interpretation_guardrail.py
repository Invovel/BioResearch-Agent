"""Prototype interpretation guardrail policy."""

RULES = [
    "result interpretation must stay artifact-grounded",
    "uncertainty language required when evidence is incomplete",
    "do not escalate research outputs into clinical diagnosis",
]

