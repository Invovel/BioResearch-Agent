# CODEX.md

BioResearch-Agent is a personal, privacy-safe biomedical research-agent project. It is intended for public portfolio work, vibe-coding experiments, and clean skill/tool orchestration demos.

This file is the primary operating guide for Codex-style coding agents working in this repository.

## Core Position

BioResearch-Agent is:

- A public-safe biomedical research assistant scaffold.
- A skill/tool orchestration demo with explicit privacy gates.
- A small Python CLI project that can be tested locally.
- A place to rebuild research-agent ideas with clean-room adapters and placeholders.

BioResearch-Agent is not:

- A clinical diagnosis system.
- A copy of a private platform.
- A production medical workflow engine.
- A repository for private data, internal tool implementations, model weights, deployment paths, logs, or credentials.

## Required Reading Order

When starting a new agent session, read these files first:

1. `README.md`
2. `SKILL.md`
3. `CODEX.md`
4. `docs/privacy_sanitization.md`
5. `docs/skills_tools_extension.md`
6. `docs/vibe_coding.md`
7. `tests/test_agent.py`

Only read external/local private projects for high-level reference when the user explicitly asks. Do not copy private implementation details into this repository.

## Project Shape

| Path | Role |
| --- | --- |
| `bioresearch_agent/schemas.py` | Public-safe dataclasses for requests, evidence, skill results, tool results, and plans. |
| `bioresearch_agent/privacy.py` | Privacy gate for likely secrets, absolute paths, patient-like IDs, and private data references. |
| `bioresearch_agent/retrieval.py` | Small dependency-free lexical retrieval over public placeholder evidence. |
| `bioresearch_agent/skills.py` | Bounded skill registry. |
| `bioresearch_agent/tools.py` | Tool registry with safe callable or placeholder tools. |
| `bioresearch_agent/planner.py` | Thin coordinator: privacy -> intent -> retrieval -> skills/tools -> structured plan. |
| `bioresearch_agent/cli.py` | Command-line entry point. |
| `docs/` | Public-safe design, privacy, and workflow documentation. |
| `tests/` | Regression tests for current behavior. |

## Development Rules

- Keep changes small and testable.
- Prefer explicit dataclasses and registries over hidden prompt rules.
- Keep skill outputs structured and reviewable.
- Keep tool behavior bounded by metadata, privacy checks, and confirmation gates.
- Do not add web UI, deployment scripts, private service routes, private assets, or production medical claims unless the user explicitly asks and the content is public-safe.
- Do not add real patient, slide, institution, server, path, model, credential, or job-log examples.
- Do not turn generated biomedical text into clinical advice.

## Skill And Tool Boundary

The intended pattern is:

```text
question
  -> privacy gate
  -> intent classification
  -> public evidence retrieval
  -> skill selection
  -> optional safe tool adapter
  -> structured plan
  -> human review
```

Skills describe capabilities. Tools perform bounded actions. A skill may recommend tools, but it must not silently execute privileged actions.

Tool classes should be one of:

- `read_only`: reads public or synthetic metadata.
- `planning`: produces plans, checklists, or reviewable structured output.
- `export`: writes safe local public artifacts.
- `adapter_stub`: documents a future integration without executing it.
- `privileged_placeholder`: requires explicit confirmation and must remain non-executing until a clean public implementation exists.

## Privacy And IP Rules

Never commit or generate:

- `.env` files or secrets.
- Real private datasets.
- Patient identifiers.
- Clinical slide files or derived private artifacts.
- Logs, caches, exports, reports, or execution traces from private systems.
- Internal API routes, server paths, model paths, or deployment details.
- Proprietary implementation code copied from another project.

Allowed public-safe content:

- Generic skill names and capability categories.
- Abstract architecture patterns.
- Clean-room stubs.
- Synthetic examples.
- Public paper metadata.
- Tests using tiny synthetic fixtures.

## Validation Commands

Use these commands from the repository root:

```powershell
python -m pytest -q
python -m bioresearch_agent --list-skills
python -m bioresearch_agent --list-tools
python -m bioresearch_agent "Plan a public literature review workflow for biomedical AI agents"
python -m bioresearch_agent "Search public papers for biomedical evidence retrieval" --allow-tools --json
```

Before a public release, also scan for sensitive files and strings:

```powershell
Get-ChildItem -Recurse -File
rg -n "\.env|patient_|private|secret|token|password|sk-|\.svs|\.xlsx|\.db|\.log" .
```

If the scan finds private terms, remove or rewrite the content instead of explaining it away.

## Commit Discipline

Good commit scopes:

- `docs: clarify privacy boundary`
- `skills: add public-safe adapter stub`
- `tools: add confirmation-gated placeholder`
- `tests: cover privacy gate`
- `cli: improve list output`

Avoid mixing documentation rewrites, registry changes, and planner behavior changes in one commit unless the user asks for a single bundled change.

## Agent Response Style

When reporting work to the user:

- Say what changed.
- Say what was intentionally excluded for privacy/IP safety.
- Say what validation ran.
- Keep the summary concise and practical.

Do not claim the project implements real clinical automation or production execution unless the code and tests actually prove it.
