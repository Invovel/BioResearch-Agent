"""Local validation entrypoint for the clean prototype."""

from __future__ import annotations

import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from agent_langgraph_prototype.orchestrator import PrototypeOrchestrator


def main() -> int:
    orchestrator = PrototypeOrchestrator()
    checks = {
        "info": orchestrator.info(),
        "tool_manifest": orchestrator.run(mode="tool_manifest"),
        "flow_plan": orchestrator.run("public biomedical workflow planning", mode="flow_plan"),
        "execute_tool_blocked": orchestrator.run(mode="execute_tool", tool_id="example_tool"),
    }
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

