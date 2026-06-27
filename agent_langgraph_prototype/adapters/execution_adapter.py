"""Execution and result-readback placeholders.

No real external tool execution is performed in BioResearch-Agent.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_langgraph_prototype.runtime_config import get_runtime_config


class ExecutionAdapter:
    def __init__(self):
        self.runtime = get_runtime_config()

    def execute_tool(
        self,
        tool_id: str,
        slide_paths: list[str],
        *,
        model_args: dict[str, Any] | None = None,
        username: str = "bioresearch_agent",
        extra_slots: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        return {
            "success": False,
            "status": "blocked_placeholder",
            "tool_id": tool_id,
            "reason": "Execution adapters are stubs in the public BioResearch-Agent project.",
            "received": {
                "input_count": len(slide_paths),
                "model_arg_keys": sorted((model_args or {}).keys()),
                "extra_slot_keys": sorted((extra_slots or {}).keys()),
                "username": username,
            },
        }

    def execute_demo_tool(
        self,
        tool_id: str,
        *,
        input_image_path: str | None = None,
        extra_slots: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        return self.execute_tool(
            tool_id,
            [input_image_path] if input_image_path else [],
            extra_slots=extra_slots,
        )

    def inspect_result_manifest(self, manifest_path: str) -> dict[str, Any]:
        path = Path(manifest_path)
        if not path.is_absolute():
            path = self.runtime.exec_base / manifest_path
        if not path.is_file():
            return {
                "status": "not_found",
                "manifest_path": str(path),
                "execution_mode": "local_placeholder_only",
            }
        return json.loads(path.read_text(encoding="utf-8"))

    def find_result_file(self, task_id: str, filename: str, *, username: str = "bioresearch_agent") -> str | None:
        candidate = self.runtime.exec_base / username / str(task_id) / filename
        return str(candidate) if candidate.is_file() else None

