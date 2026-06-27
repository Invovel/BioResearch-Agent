"""Small smoke entrypoint for the isolated prototype."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from agent_langgraph_prototype.orchestrator import PrototypeOrchestrator


def main():
    orchestrator = PrototypeOrchestrator()
    payload = {
        "runtime": orchestrator.info(),
        "tool_manifest_preview": orchestrator.run(mode="tool_manifest", graph_backend="langgraph"),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

