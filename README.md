# BioResearch-Agent

> A privacy-safe reference discovery, neutral marking, and evidence-check workflow for biomedical vibe coding.

BioResearch-Agent is a compact Python project for public-safe biomedical literature work. Its core loop is:

```text
search references -> attach neutral markers -> verify marker support -> compare same-marker papers -> expand search
```

The project deliberately stays narrower than a full research platform. It does not rank papers as good/bad, does not claim clinical validity, and does not copy private project code, data, model paths, logs, or tool implementations.

## What Stays

| Surface | Implemented items |
| --- | --- |
| Skills | `reference_mapping`, `protocol_checklist`, `research_plan` |
| Tools | `reference_search`, `reference_mark`, `marker_verify`, `marker_compare`, `markdown_brief_export` |
| Safety | `PrivacyGate` blocks likely secrets, paths, patient-like IDs, and private data file references |
| Retrieval | dependency-free public placeholder reference search, replaceable by future PubMed/arXiv adapters |
| CLI | list skills/tools, run reference workflow, optional JSON output |

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
```

## Code Structure

| Path | Purpose |
| --- | --- |
| `bioresearch_agent/schemas.py` | Public-safe dataclasses for requests, evidence, markers, verifications, tool results, skill results, and plans. |
| `bioresearch_agent/privacy.py` | Privacy gate for secrets, absolute paths, patient-like IDs, and private file references. |
| `bioresearch_agent/retrieval.py` | Small dependency-free lexical retriever over public placeholder references. |
| `bioresearch_agent/reference_workflow.py` | Reference search, neutral marking, marker verification, and same-marker comparison logic. |
| `bioresearch_agent/skills.py` | Skill registry and default skills. |
| `bioresearch_agent/tools.py` | Tool registry and safe default tools. |
| `bioresearch_agent/planner.py` | Thin coordinator that routes query -> privacy -> retrieval -> markers/tools. |
| `bioresearch_agent/cli.py` | Command-line interface. |
| `agent_langgraph_prototype/` | Clean-room graph/agent/skill/tool prototype with local stubs only. |

## Marker Policy

- A marker is a neutral grouping label, not a quality score.
- `marker_verify` checks whether the marker is supported by visible metadata such as title, abstract, and tags.
- Verification does not prove the full paper is correct.
- Same-marker comparison is used to find shared assumptions, differences, and expansion queries.

## Docs

- [SKILL.md](SKILL.md): skill-style entrypoint for vibe coding.
- [CODEX.md](CODEX.md): operating guide for Codex-style coding agents.
- [CLAUDE.md](CLAUDE.md): short Claude-compatible pointer to the same rules.
- [docs/skills_tools_extension.md](docs/skills_tools_extension.md): extension rules.
- [docs/privacy_sanitization.md](docs/privacy_sanitization.md): sanitization rules.
- [docs/vibe_coding.md](docs/vibe_coding.md): working loop.
- [docs/one_sentence_summary.md](docs/one_sentence_summary.md): one-line report.
- [agent_langgraph_prototype/README.md](agent_langgraph_prototype/README.md): clean local graph prototype notes.
