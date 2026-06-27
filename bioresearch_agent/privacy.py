from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PrivacyFinding:
    kind: str
    match: str
    message: str


class PrivacyGate:
    """Small privacy scanner for public demos and portfolio artifacts."""

    _PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
        ("secret", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*\S+"), "Possible secret."),
        ("absolute_path", re.compile(r"(?i)([a-z]:\\|/(?:home|mnt|users|var|opt)/)"), "Absolute local path."),
        ("patient_id", re.compile(r"(?i)\b(patient|subject|case)[_-]?\d{3,}\b"), "Possible subject identifier."),
        ("private_file", re.compile(r"(?i)\.(svs|kfb|ndpi|mrxs|xlsx|sqlite|db)\b"), "Private or heavy data file."),
        ("internal_marker", re.compile(r"(?i)\b(internal|confidential|proprietary|private[-_ ]project)\b"), "Internal marker."),
    )

    def scan(self, text: str) -> list[PrivacyFinding]:
        findings: list[PrivacyFinding] = []
        for kind, pattern, message in self._PATTERNS:
            for match in pattern.finditer(text):
                findings.append(PrivacyFinding(kind=kind, match=match.group(0), message=message))
        return findings

    def assert_public_safe(self, text: str) -> None:
        findings = self.scan(text)
        if findings:
            first = findings[0]
            raise ValueError(f"Privacy gate blocked {first.kind}: {first.message}")
