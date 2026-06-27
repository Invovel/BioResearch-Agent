from __future__ import annotations

import argparse
import json

from .planner import BioResearchAgent
from .schemas import ResearchRequest
from .skills import SkillRegistry
from .tools import ToolRegistry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BioResearch-Agent skills & tools kit.")
    parser.add_argument("query", nargs="?", help="Public-safe biomedical research question.")
    parser.add_argument("--role", default="researcher", help="User role label.")
    parser.add_argument("--upload", action="append", default=None, help="Uploaded public-safe file name or label. Repeatable.")
    parser.add_argument("--data-note", action="append", default=None, help="User observation about uploaded image/data. Repeatable.")
    parser.add_argument("--allow-tools", action="store_true", help="Allow low-risk public-safe tool calls.")
    parser.add_argument("--reference-workflow", action="store_true", help="Run the data-grounded literature validation tool chain.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--list-skills", action="store_true", help="List built-in skills and exit.")
    parser.add_argument("--list-tools", action="store_true", help="List built-in tools and exit.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.list_skills:
        for spec in SkillRegistry.defaults().list_specs():
            print(f"{spec.skill_id}\t{spec.purpose}")
        return 0
    if args.list_tools:
        for spec in ToolRegistry.defaults().list_specs():
            print(f"{spec.tool_id}\t{spec.description}")
        return 0
    if not args.query:
        build_parser().error("query is required unless --list-skills or --list-tools is used")

    agent = BioResearchAgent()
    plan = agent.plan(
        ResearchRequest(
            query=args.query,
            user_role=args.role,
            uploaded_files=tuple(args.upload or ()),
            data_notes=tuple(args.data_note or ()),
            allow_tool_execution=args.allow_tools or args.reference_workflow,
        )
    )
    if args.json:
        print(json.dumps(plan.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(f"Intent: {plan.intent}")
        print("Recommended steps:")
        for step in plan.recommended_steps:
            print(f"- {step}")
        print("Human review required: yes")
    return 0
