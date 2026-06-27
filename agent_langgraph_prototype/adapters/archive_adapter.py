"""Local JSON archive adapter for synthetic sessions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from agent_langgraph_prototype.runtime_config import get_runtime_config


class ArchiveAdapter:
    def __init__(self, data_root: Path | None = None):
        runtime = get_runtime_config()
        self.data_root = Path(data_root or runtime.archive_root)
        self.data_root.mkdir(parents=True, exist_ok=True)

    def archive_session(self, session_data: dict[str, Any]) -> str:
        session_id = str(session_data.get("session_id") or uuid4().hex)
        path = self.data_root / f"{session_id}.json"
        safe_payload = {
            "session_id": session_id,
            "summary": str(session_data.get("summary") or ""),
            "messages": list(session_data.get("messages") or []),
            "privacy": "synthetic_or_public_only",
        }
        path.write_text(json.dumps(safe_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)

    def get_session_record(self, session_id: str, *, user_id: str | None = None) -> dict[str, Any] | None:
        path = self.data_root / f"{session_id}.json"
        if not path.is_file():
            return None
        record = json.loads(path.read_text(encoding="utf-8"))
        if user_id and record.get("user_id") not in ("", None, user_id):
            return None
        return record

    def list_user_records(self, user_id: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for path in sorted(self.data_root.glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            if record.get("user_id") in ("", None, user_id):
                records.append(record)
        return records

