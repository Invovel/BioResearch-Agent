# BioResearch-Agent

> A privacy-safe reference discovery, neutral marking, and evidence-check workflow for biomedical vibe coding.

BioResearch-Agent is a compact Python project for public-safe biomedical literature work. Its core loop is:

```text
search references -> attach neutral markers -> verify marker support -> compare same-marker papers -> expand search
```

The full target workflow is organized in [docs/end_to_end_workflow.md](docs/end_to_end_workflow.md). Its architecture is clean-room informed by mature academic-writing skill repos and by high-level framework lessons from `D:\Download\PathoFlow`: layered contracts, source provenance, execution gates, observability, benchmark checks, and explicit failure paths. It does not copy PathoFlow code, private assets, logs, manifests, data, prompts, or credentials.

```text
question -> PubMed/arXiv/bioRxiv retrieval -> entity extraction -> cited summary -> next workflow -> manuscript package -> MemoryWeaver trace -> report
```

The project deliberately stays narrower than a full research platform. It does not rank papers as good/bad, does not claim clinical validity, and does not copy private project code, data, model paths, logs, or tool implementations.

## What Stays

| Surface | Implemented items |
| --- | --- |
| Skills | `reference_mapping`, `protocol_checklist`, `research_plan` |
| Tools | `reference_search`, `reference_mark`, `marker_verify`, `marker_compare`, `markdown_brief_export` |
| Safety | `PrivacyGate` blocks likely secrets, paths, patient-like IDs, and private data file references |
| Retrieval | dependency-free public placeholder reference search plus optional live PubMed/arXiv/bioRxiv metadata adapters |
| Writing workflow | strategist/composer manuscript planning, IMRAD outline, top-journal narrative checks, claim-citation QA, figure/table audit, reviewer-response plan |
| Framework contracts | stage-level checks for privacy, retrieval provenance, entity extraction, summary, next workflow, manuscript workflow, and MemoryWeaver trace |
| CLI | list skills/tools, run reference workflow, end-to-end report, live-source mode, benchmark mode, optional JSON output |

## What Is Removed

- Web interface claims.
- Large agent-platform roadmap.
- Private project names and internal tool implementations.
- Real datasets, logs, model paths, deployment paths, and full tool manifests.
- Clinical diagnosis or production medical-platform claims.

## Quick Start

```powershell
cd BioResearch-Agent
python -m pytest -q
python -m bioresearch_agent --list-skills
python -m bioresearch_agent --list-tools
python -m bioresearch_agent "Compare papers with the same marker for biomedical agent workflows"
python -m bioresearch_agent "Search public papers for RAG evidence retrieval" --reference-workflow --json
python -m bioresearch_agent "How do BRCA1 breast cancer papers connect drugs, datasets, and RAG methods?" --end-to-end-report
python -m bioresearch_agent "BRCA1 breast cancer PARP inhibitor datasets RAG" --end-to-end-report --live-sources
python -m bioresearch_agent --benchmark
python -m bioresearch_agent --benchmark --live-sources --json
python -m bioresearch_agent --skill-pack github:aipoch/medical-research-skills --list-external-skills
python -m bioresearch_agent --skill-pack github:aipoch/medical-research-skills --langgraph-node-specs --json
python -m bioresearch_agent --list-workflows
python -m bioresearch_agent --workflow-specs --langgraph-node-specs --json
```

## Code Structure

| Path | Purpose |
| --- | --- |
| `bioresearch_agent/schemas.py` | Public-safe dataclasses for requests, evidence, markers, verifications, tool results, skill results, and plans. |
| `bioresearch_agent/privacy.py` | Privacy gate for secrets, absolute paths, patient-like IDs, and private file references. |
| `bioresearch_agent/retrieval.py` | Small dependency-free lexical retriever over public placeholder references. |
| `bioresearch_agent/live_sources.py` | Dependency-free public PubMed, arXiv, and bioRxiv metadata adapters. |
| `bioresearch_agent/reference_workflow.py` | Reference search, neutral marking, marker verification, and same-marker comparison logic. |
| `bioresearch_agent/end_to_end_workflow.py` | Full research-to-report-to-manuscript workflow with placeholder or live-source retrieval and MemoryWeaver trace. |
| `bioresearch_agent/workflow_contracts.py` | Clean-room stage contracts and checks inspired by mature framework boundaries. |
| `bioresearch_agent/external_skills.py` | Local or GitHub `SKILL.md` discovery plus LangGraph node-spec generation for external skill packs. |
| `bioresearch_agent/benchmark.py` | Independent workflow benchmark for retrieval, traceability, entity extraction, MemoryWeaver, and manuscript package coverage. |
| `bioresearch_agent/skills.py` | Skill registry and default skills. |
| `bioresearch_agent/tools.py` | Tool registry and safe default tools. |
| `bioresearch_agent/skill_workflows.py` | LangGraph-style internal skill workflows: each skill owns a workflow, tools, gates, edges, and memory policy. |
| `bioresearch_agent/workflow_runtime.py` | Lightweight local runtime that executes skill workflow nodes against the tool registry. |
| `bioresearch_agent/planner.py` | Thin coordinator that routes query -> privacy -> retrieval -> markers/tools. |
| `bioresearch_agent/cli.py` | Command-line interface. |
| `agent_langgraph_prototype/` | Clean-room graph/agent/skill/tool prototype with local stubs only. |

## Marker Policy

- A marker is a neutral grouping label, not a quality score.
- `marker_verify` checks whether the marker is supported by visible metadata such as title, abstract, and tags.
- Verification does not prove the full paper is correct.
- Same-marker comparison is used to find shared assumptions, differences, and expansion queries.

## Manuscript Workflow Policy

- Manuscript outputs are strategy, outline, and QA scaffolds, not submission-ready papers.
- The workflow borrows public design patterns from mature academic-writing skill projects, but does not copy private prompts, external implementation code, or copyrighted prose.
- Top-journal and Nature-family language means restrained evidence-first writing discipline, not imitation of specific articles.
- Every substantive manuscript claim should map to a reference ID, entity mention, marker verification, or pending-review tag.

## Docs

- [SKILL.md](SKILL.md): skill-style entrypoint for vibe coding.
- [CODEX.md](CODEX.md): operating guide for Codex-style coding agents.
- [CLAUDE.md](CLAUDE.md): short Claude-compatible pointer to the same rules.
- [docs/skills_tools_extension.md](docs/skills_tools_extension.md): extension rules.
- [docs/end_to_end_workflow.md](docs/end_to_end_workflow.md): full public-safe research workflow from question to report.
- [docs/skill_pack_integration.md](docs/skill_pack_integration.md): external Codex/Claude skill-pack mounting, LangGraph node specs, and Weaver-compatible path patterns.
- [docs/privacy_sanitization.md](docs/privacy_sanitization.md): sanitization rules.
- [docs/vibe_coding.md](docs/vibe_coding.md): working loop.
- [docs/one_sentence_summary.md](docs/one_sentence_summary.md): one-line report.
- [agent_langgraph_prototype/README.md](agent_langgraph_prototype/README.md): clean local graph prototype notes.
