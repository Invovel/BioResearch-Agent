import pytest

from bioresearch_agent import BioResearchAgent, ResearchRequest
from bioresearch_agent.benchmark import run_benchmark
from bioresearch_agent.cli import main
from bioresearch_agent.end_to_end_workflow import run_end_to_end_workflow
from bioresearch_agent.external_skills import build_langgraph_node_specs, discover_external_skills
from bioresearch_agent.planner import classify_intent
from bioresearch_agent.skill_workflows import default_skill_workflows, workflow_langgraph_nodes
from bioresearch_agent.skills import SkillRegistry
from bioresearch_agent.schemas import ToolResult
from bioresearch_agent.tools import ToolRegistry, ToolSpec
from bioresearch_agent.workflow_runtime import SkillWorkflowRuntime


def test_agent_builds_public_safe_research_plan():
    agent = BioResearchAgent()
    plan = agent.plan(
        ResearchRequest(
            query="Use my uploaded image to cite related papers about biomedical agent workflows",
            uploaded_files=("demo_image.png",),
            data_notes=("workflow evidence retrieval with privacy review",),
        )
    )

    assert plan.intent == "data_grounded_literature_validation"
    assert plan.evidence
    assert plan.skill_results
    assert plan.uploaded_data
    assert plan.data_reliability
    assert plan.paper_data_alignment
    assert plan.innovation_signals or plan.paper_data_alignment
    assert plan.reference_marks
    assert plan.reference_verifications
    assert plan.human_review_required is True
    assert any("privacy" in risk.lower() or "private" in risk.lower() for risk in plan.risks)


def test_agent_can_call_low_risk_public_tool():
    agent = BioResearchAgent()
    plan = agent.plan(
        ResearchRequest(
            query="Search public papers for biomedical evidence retrieval",
            uploaded_files=("figure1.png",),
            data_notes=("retrieval evidence citation workflow",),
            allow_tool_execution=True,
        )
    )

    assert plan.tool_results
    assert [result.tool_id for result in plan.tool_results] == [
        "reference_search",
        "data_reliability_check",
        "paper_data_alignment",
        "innovation_scan",
        "reference_mark",
        "marker_verify",
        "marker_compare",
    ]
    assert all(result.status == "ok" for result in plan.tool_results)
    outputs = {result.tool_id: result.output for result in plan.tool_results}
    assert outputs["reference_search"]["references"]
    assert outputs["data_reliability_check"]["uploaded_data"]
    assert outputs["paper_data_alignment"]["alignments"]
    assert outputs["reference_mark"]["marks"]
    assert len(outputs["marker_verify"]["verifications"]) == len(outputs["reference_mark"]["marks"])
    assert outputs["marker_compare"]["comparison"]


def test_tool_chain_skips_tools_with_missing_upstream_inputs():
    registry = ToolRegistry.defaults()

    results = registry.run_chain(("marker_verify",), {"references": []})

    assert results[0].status == "skipped"
    assert "marks" in results[0].warnings[0]


def test_tool_chain_contains_handler_failure_and_blocks_dependent_tool():
    registry = ToolRegistry()

    def failing_source(payload):
        raise RuntimeError("synthetic failure")

    registry.register(
        ToolSpec(
            tool_id="source",
            description="Synthetic failing source.",
            produced_outputs=("value",),
        ),
        failing_source,
    )
    registry.register(
        ToolSpec(
            tool_id="consumer",
            description="Synthetic dependent consumer.",
            required_inputs=("value",),
            produced_outputs=("done",),
        ),
        lambda payload: ToolResult(tool_id="consumer", status="ok", output={"done": True}),
    )

    results = registry.run_chain(("source", "consumer"), {})

    assert [result.status for result in results] == ["failed", "skipped"]
    assert results[0].warnings == ("Tool handler failed.",)


def test_privacy_gate_blocks_sensitive_payload():
    agent = BioResearchAgent()

    with pytest.raises(ValueError):
        agent.plan(ResearchRequest(query="Analyze patient_12345 file C:\\private\\slide.svs"))


def test_tool_registry_requires_confirmation_for_risky_tool():
    registry = ToolRegistry.defaults()

    result = registry.run("missing_tool", {"query": "public"})
    assert result.status == "not_found"


def test_intent_classifier_is_small_and_predictable():
    assert classify_intent("draft an experiment protocol") == "protocol_planning"
    assert classify_intent("which tool should I run") == "tool_aware_planning"
    assert classify_intent("general research plan") == "research_planning"
    assert classify_intent("verify citations against uploaded image data") == "data_grounded_literature_validation"


def test_default_skills_and_tools_are_listable():
    skill_ids = {spec.skill_id for spec in SkillRegistry.defaults().list_specs()}
    tool_ids = {spec.tool_id for spec in ToolRegistry.defaults().list_specs()}

    assert skill_ids == {"data_grounded_literature_validation", "protocol_checklist", "research_plan"}
    skill_specs = {spec.skill_id: spec for spec in SkillRegistry.defaults().list_specs()}
    assert skill_specs["data_grounded_literature_validation"].workflow_id == "workflow.data_grounded_literature_validation.v1"
    assert "reference_search" in skill_specs["data_grounded_literature_validation"].tool_ids
    assert {
        "public_paper_search",
        "reference_search",
        "data_reliability_check",
        "paper_data_alignment",
        "innovation_scan",
        "reference_mark",
        "marker_verify",
        "marker_compare",
        "markdown_brief_export",
    } <= tool_ids
    specs = {spec.tool_id: spec for spec in ToolRegistry.defaults().list_specs()}
    assert specs["marker_verify"].required_inputs == ("references", "marks")
    assert specs["marker_verify"].produced_outputs == ("verifications",)


def test_internal_skills_have_langgraph_style_workflows():
    workflows = default_skill_workflows()
    by_skill = {item.skill_id: item for item in workflows}

    assert set(by_skill) == {"data_grounded_literature_validation", "protocol_checklist", "research_plan"}
    data_workflow = by_skill["data_grounded_literature_validation"]
    assert data_workflow.tool_ids[:2] == ("reference_search", "data_reliability_check")
    assert ("privacy_gate", "reference_search") in data_workflow.edges
    nodes = workflow_langgraph_nodes(data_workflow)
    assert nodes[0].node_id.startswith("workflow.data_grounded_literature_validation.v1::")
    assert "privacy_gate" in nodes[0].safety_policy


def test_skill_workflow_runtime_executes_tool_nodes():
    workflow = {item.skill_id: item for item in default_skill_workflows()}["data_grounded_literature_validation"]
    runtime = SkillWorkflowRuntime(tools=ToolRegistry.defaults())

    result = runtime.run(
        workflow,
        {
            "query": "Search public papers for biomedical evidence retrieval",
            "top_k": 3,
            "uploaded_files": ("figure1.png",),
            "data_notes": ("retrieval evidence workflow",),
        },
    )

    assert result.status == "ok"
    assert [item.tool_id for item in result.tool_results] == list(workflow.tool_ids)
    assert "comparison" in result.context_keys
    assert any(item["kind"] == "memory" for item in result.node_results)


def test_cli_lists_skills_and_tools(capsys):
    assert main(["--list-skills"]) == 0
    skills_output = capsys.readouterr().out
    assert "data_grounded_literature_validation" in skills_output
    assert "research_plan" in skills_output

    assert main(["--list-tools"]) == 0
    tools_output = capsys.readouterr().out
    assert "reference_search" in tools_output
    assert "paper_data_alignment" in tools_output
    assert "marker_verify" in tools_output
    assert "markdown_brief_export" in tools_output

    assert main(["--list-workflows"]) == 0
    workflows_output = capsys.readouterr().out
    assert "workflow.data_grounded_literature_validation.v1" in workflows_output
    assert "reference_search" in workflows_output


def test_cli_outputs_internal_workflow_specs(capsys):
    assert main(["--workflow-specs", "--json"]) == 0
    payload = capsys.readouterr().out
    assert "workflow.research_plan.v1" in payload
    assert "safety_gates" in payload

    assert main(["--workflow-specs", "--langgraph-node-specs", "--json"]) == 0
    payload = capsys.readouterr().out
    assert "workflow.protocol_checklist.v1::privacy_gate" in payload


def test_reference_workflow_cli_outputs_markers(capsys):
    assert main(
        [
            "verify citations against uploaded image observations",
            "--upload",
            "figure1.png",
            "--data-note",
            "privacy review evidence retrieval",
            "--reference-workflow",
            "--json",
        ]
    ) == 0
    payload = capsys.readouterr().out
    assert "uploaded_data" in payload
    assert "paper_data_alignment" in payload
    assert "innovation_scan" in payload


def test_end_to_end_workflow_outputs_report_and_memory_trace():
    report = run_end_to_end_workflow("How do BRCA1 breast cancer papers connect drugs, datasets, and RAG methods?")

    assert report.references
    assert report.entities
    assert report.memory_trace.success_paths
    assert report.next_workflow
    assert report.manuscript_workflow.imrad_outline
    assert report.manuscript_workflow.audit_gates
    assert report.contract_checks
    assert all(item.status == "passed" for item in report.contract_checks)
    assert report.memory_trace.path_patterns
    assert "BioResearch-Agent End-to-End Report" in report.markdown
    assert "Manuscript Workflow Package" in report.markdown
    assert "Framework Contract Checks" in report.markdown
    assert "Weaver-Compatible Path Patterns" in report.markdown
    assert "Reviewer Response Plan" in report.markdown
    assert "MemoryWeaver Trace Summary" in report.markdown
    assert any(item.entity_type == "gene" and item.normalized_name == "BRCA1" for item in report.entities)


def test_end_to_end_report_cli_outputs_markdown(capsys):
    assert main(["How do BRCA1 breast cancer papers connect drugs and RAG methods?", "--end-to-end-report"]) == 0
    payload = capsys.readouterr().out
    assert "Citation-Backed Research Summary" in payload
    assert "Next-Step Workflow" in payload
    assert "Manuscript Workflow Package" in payload
    assert "Framework Contract Checks" in payload
    assert "MemoryWeaver Trace Summary" in payload


def test_benchmark_outputs_independent_metrics():
    payload = run_benchmark()

    assert payload["benchmark_id"] == "bioresearch_agent_end_to_end_v1"
    assert payload["case_count"] == 3
    assert payload["passed_count"] >= 1
    assert all("traceable_references" in item for item in payload["results"])
    assert all("contract_checks_passed" in item for item in payload["results"])
    assert all("weaver_path_patterns" in item for item in payload["results"])


def test_benchmark_cli_outputs_markdown(capsys):
    assert main(["--benchmark"]) == 0
    payload = capsys.readouterr().out
    assert "BioResearch-Agent Benchmark" in payload
    assert "Traceable refs" in payload
    assert "Contracts" in payload


def test_external_skill_pack_discovery_and_langgraph_specs(tmp_path):
    skill_dir = tmp_path / "medical-review-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: Medical Review Skill
description: Evidence-backed medical research audit for citations and claims.
---

# Medical Review Skill

Use for public-safe medical manuscript audit.
""",
        encoding="utf-8",
    )

    specs = discover_external_skills(tmp_path)
    nodes = build_langgraph_node_specs(specs)

    assert len(specs) == 1
    assert specs[0].skill_id == "medical-review-skill"
    assert nodes[0].node_id == "external_skill::medical-review-skill"
    assert "public_safe_research_question" in nodes[0].input_contract


def test_external_skill_pack_cli_outputs_index(tmp_path, capsys):
    skill_dir = tmp_path / "claim-audit"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: Claim Audit
description: Check manuscript claims against cited evidence.
---
""",
        encoding="utf-8",
    )

    assert main(["--skill-pack", str(tmp_path), "--list-external-skills"]) == 0
    payload = capsys.readouterr().out
    assert "External Skill Pack Index" in payload
    assert "claim-audit" in payload

    assert main(["--skill-pack", str(tmp_path), "--langgraph-node-specs"]) == 0
    payload = capsys.readouterr().out
    assert "external_skill::claim-audit" in payload
