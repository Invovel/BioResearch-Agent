from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .end_to_end_workflow import run_end_to_end_workflow


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    query: str
    expected_entities: tuple[str, ...]
    min_references: int = 1


DEFAULT_BENCHMARK_CASES: tuple[BenchmarkCase, ...] = (
    BenchmarkCase(
        case_id="brca1_breast_cancer",
        query="BRCA1 breast cancer PARP inhibitor datasets RAG",
        expected_entities=("BRCA1", "breast cancer"),
    ),
    BenchmarkCase(
        case_id="spatial_tme",
        query="spatial transcriptomics tumor microenvironment TCGA GEO biomedical workflow",
        expected_entities=("spatial transcriptomics", "tumor microenvironment"),
    ),
    BenchmarkCase(
        case_id="biomedical_rag",
        query="retrieval augmented generation biomedical literature entity extraction citation",
        expected_entities=("retrieval augmented generation", "entity extraction"),
    ),
)


def run_benchmark(*, live_sources: bool = False, top_k: int = 6) -> dict[str, Any]:
    """Run an independent workflow benchmark and return JSON-serializable metrics."""

    results = []
    for case in DEFAULT_BENCHMARK_CASES:
        report = run_end_to_end_workflow(case.query, top_k=top_k, live_sources=live_sources)
        entity_names = {item.normalized_name for item in report.entities}
        source_names = {doc.source for doc in report.references}
        traceable_refs = [
            doc.doc_id
            for doc in report.references
            if doc.url or doc.doi or doc.source_id or doc.doc_id.startswith(("PMID:", "arXiv:", "bioRxiv:"))
        ]
        expected_hits = sorted(set(case.expected_entities) & entity_names)
        missing_expected = sorted(set(case.expected_entities) - entity_names)
        passed = (
            len(report.references) >= case.min_references
            and bool(traceable_refs)
            and not missing_expected
            and all(check.status == "passed" for check in report.contract_checks)
            and bool(report.summary)
            and bool(report.next_workflow)
            and bool(report.manuscript_workflow.imrad_outline)
        )
        contract_failures = {
            check.stage: list(check.missing)
            for check in report.contract_checks
            if check.status != "passed"
        }
        results.append(
            {
                "case_id": case.case_id,
                "query": case.query,
                "passed": passed,
                "retrieved_references": len(report.references),
                "source_count": len(source_names),
                "sources": sorted(source_names),
                "traceable_references": len(traceable_refs),
                "extracted_entities": sorted(entity_names),
                "expected_entity_hits": expected_hits,
                "missing_expected_entities": missing_expected,
                "memory_success_paths": len(report.memory_trace.success_paths),
                "memory_failure_paths": len(report.memory_trace.failure_paths),
                "weaver_path_patterns": len(report.memory_trace.path_patterns),
                "has_manuscript_package": bool(report.manuscript_workflow.imrad_outline),
                "contract_checks_passed": len(report.contract_checks) - len(contract_failures),
                "contract_checks_total": len(report.contract_checks),
                "contract_failures": contract_failures,
                "warnings": list(report.memory_trace.warnings),
            }
        )
    passed_count = sum(1 for item in results if item["passed"])
    return {
        "benchmark_id": "bioresearch_agent_end_to_end_v1",
        "mode": "live public adapters" if live_sources else "public-safe placeholder adapters",
        "case_count": len(results),
        "passed_count": passed_count,
        "failed_count": len(results) - passed_count,
        "results": results,
    }


def render_benchmark_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# BioResearch-Agent Benchmark",
        "",
        f"- Benchmark ID: `{payload['benchmark_id']}`",
        f"- Mode: {payload['mode']}",
        f"- Cases: {payload['case_count']}",
        f"- Passed: {payload['passed_count']}",
        f"- Failed: {payload['failed_count']}",
        "",
        "| Case | Passed | References | Sources | Traceable refs | Contracts | Missing expected entities |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in payload["results"]:
        missing = ", ".join(item["missing_expected_entities"]) or "none"
        lines.append(
            f"| {item['case_id']} | {item['passed']} | {item['retrieved_references']} | "
            f"{item['source_count']} | {item['traceable_references']} | "
            f"{item['contract_checks_passed']}/{item['contract_checks_total']} | {missing} |"
        )
    lines.extend(["", "## Case Details", ""])
    for item in payload["results"]:
        lines.extend(
            [
                f"### {item['case_id']}",
                "",
                f"- Query: {item['query']}",
                f"- Sources: {', '.join(item['sources']) or 'none'}",
                f"- Extracted entities: {', '.join(item['extracted_entities']) or 'none'}",
                f"- Memory paths: {item['memory_success_paths']} success / {item['memory_failure_paths']} failure",
                f"- Manuscript package: {'yes' if item['has_manuscript_package'] else 'no'}",
                f"- Contract failures: {item['contract_failures'] or 'none'}",
                "",
            ]
        )
    return "\n".join(lines)
