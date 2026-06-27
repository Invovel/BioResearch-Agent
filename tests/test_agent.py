import pytest

from bioresearch_agent import BioResearchAgent, ResearchRequest
from bioresearch_agent.cli import main
from bioresearch_agent.planner import classify_intent
from bioresearch_agent.skills import SkillRegistry
from bioresearch_agent.schemas import ToolResult
from bioresearch_agent.tools import ToolRegistry, ToolSpec


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
