from __future__ import annotations

import argparse
import json

from .benchmark import render_benchmark_markdown, run_benchmark
from .end_to_end_workflow import run_end_to_end_workflow
from .external_skills import build_langgraph_node_specs, discover_external_skills, render_external_skill_index
from .planner import BioResearchAgent
from .schemas import ResearchRequest
from .skill_workflows import default_skill_workflows, workflow_langgraph_nodes
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
    parser.add_argument("--end-to-end-report", action="store_true", help="Run the complete public-safe placeholder workflow and print a report.")
    parser.add_argument("--live-sources", action="store_true", help="Use live PubMed/arXiv/bioRxiv public adapters for end-to-end reports or benchmarks.")
    parser.add_argument("--benchmark", action="store_true", help="Run the independent BioResearch-Agent benchmark and exit.")
    parser.add_argument("--skill-pack", action="append", default=None, help="Path or github:owner/repo reference to an external Codex/Claude-style skill pack root. Repeatable.")
    parser.add_argument("--list-external-skills", action="store_true", help="List discovered external SKILL.md entries and exit.")
    parser.add_argument("--langgraph-node-specs", action="store_true", help="Print adapter-neutral LangGraph node specs for discovered external skills.")
    parser.add_argument("--list-workflows", action="store_true", help="List internal skill workflows and their tool chains.")
    parser.add_argument("--workflow-specs", action="store_true", help="Print internal skill workflow specs for LangGraph-style builders.")
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
    if args.list_workflows:
        for spec in default_skill_workflows():
            print(f"{spec.workflow_id}\t{spec.skill_id}\ttools={','.join(spec.tool_ids) or 'none'}")
        return 0
    if args.workflow_specs:
        workflows = default_skill_workflows()
        if args.langgraph_node_specs:
            payload = [node.to_dict() for workflow in workflows for node in workflow_langgraph_nodes(workflow)]
        else:
            payload = [workflow.to_dict() for workflow in workflows]
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            for workflow in workflows:
                print(f"{workflow.workflow_id}\t{workflow.description}")
        return 0
    if args.benchmark:
        payload = run_benchmark(live_sources=args.live_sources)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(render_benchmark_markdown(payload))
        return 0
    if args.list_external_skills or args.langgraph_node_specs:
        specs = tuple(
            spec
            for root in (args.skill_pack or ())
            for spec in discover_external_skills(root, source=root)
        )
        if args.json:
            payload = [spec.to_dict() for spec in build_langgraph_node_specs(specs)] if args.langgraph_node_specs else [spec.to_dict() for spec in specs]
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        elif args.langgraph_node_specs:
            for spec in build_langgraph_node_specs(specs):
                print(f"{spec.node_id}\t{spec.trigger_summary}")
        else:
            print(render_external_skill_index(specs, query=args.query or ""))
        return 0
    if not args.query:
        build_parser().error("query is required unless --list-skills or --list-tools is used")

    if args.end_to_end_report:
        report = run_end_to_end_workflow(args.query, live_sources=args.live_sources)
        if args.json:
            print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(report.markdown)
        return 0

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
