"""Runtime configuration for the clean local prototype."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_RUNTIME_ROOT = Path(".runtime") / "agent_langgraph_prototype"


@dataclass(frozen=True)
class PrototypeRuntimeConfig:
    runtime_root: Path
    data_root: Path
    exec_base: Path
    archive_root: Path
    traces_root: Path


def get_runtime_config() -> PrototypeRuntimeConfig:
    root = Path(os.environ.get("BIORESEARCH_AGENT_RUNTIME_ROOT") or DEFAULT_RUNTIME_ROOT)
    root = root.resolve()
    data_root = root / "data"
    exec_base = root / "executions"
    archive_root = data_root / "session_archive"
    traces_root = data_root / "traces"
    for path in (root, data_root, exec_base, archive_root, traces_root):
        path.mkdir(parents=True, exist_ok=True)
    return PrototypeRuntimeConfig(
        runtime_root=root,
        data_root=data_root,
        exec_base=exec_base,
        archive_root=archive_root,
        traces_root=traces_root,
    )

