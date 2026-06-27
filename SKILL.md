---
name: bioresearch-agent
description: Privacy-safe biomedical reference workflow for searching papers, attaching neutral markers, checking marker support, and comparing same-marker references.
---

# BioResearch-Agent Skill

Use this project when you want a small public-safe biomedical reference workflow helper.

## What It Provides

- Skill registry for bounded reference-mapping capabilities.
- Tool registry for public-safe search, marking, verification, and comparison tools.
- Privacy gate before planning or tool execution.
- Lightweight public reference retrieval.
- CLI for vibe-coding loops.

## Default Skills

- `reference_mapping`
- `protocol_checklist`
- `research_plan`

## Default Tools

- `reference_search`
- `reference_mark`
- `marker_verify`
- `marker_compare`
- `markdown_brief_export`

## Safety Rule

Do not pass private project files, patient identifiers, deployment paths, keys, logs, or proprietary tool manifests into this project.

## Marker Rule

Markers are neutral grouping labels. They do not mean a paper is good, bad, strong, weak, correct, or incorrect. `marker_verify` only checks whether visible metadata supports the marker.

## Quick Commands

```powershell
python -m bioresearch_agent --list-skills
python -m bioresearch_agent --list-tools
python -m bioresearch_agent "compare papers with the same marker for RAG evidence retrieval"
python -m bioresearch_agent "search public papers for biomedical evidence retrieval" --reference-workflow --json
```
