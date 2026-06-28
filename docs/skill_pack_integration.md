# External Skill Pack Integration

BioResearch-Agent is intended to host and route external skill collections, not rewrite every academic or biomedical workflow skill locally.

## Design Principle

Use external Codex/Claude-style skills as mounted capabilities:

```text
external SKILL.md collection
  -> skill index
  -> LangGraph node specs
  -> BioResearch-Agent workflow contracts
  -> MemoryWeaver-compatible path patterns
  -> benchmark feedback
```

Internal BioResearch-Agent skills use the same shape:

```text
skill
  -> workflow_id
  -> graph nodes and edges
  -> corresponding tool chain
  -> safety gates
  -> memory policy
```

Inspect internal workflows:

```powershell
python -m bioresearch_agent --list-workflows
python -m bioresearch_agent --workflow-specs --json
python -m bioresearch_agent --workflow-specs --langgraph-node-specs --json
```

At runtime, BioResearch-Agent executes internal skills through a lightweight graph runner:

```text
SkillWorkflowRuntime
  -> gate nodes: privacy and safety checks
  -> tool nodes: ToolRegistry-backed adapters
  -> skill nodes: reasoning/scaffold handlers
  -> memory nodes: MemoryWeaver-compatible trace layer
```

This local runner is intentionally small. A real LangGraph app can consume the same `SkillWorkflowSpec` and `LangGraphNodeSpec` payloads and replace the local runner with compiled graph execution.

This keeps the project small while letting it learn from mature skill ecosystems.

## Supported Skill Pack Inputs

Local skill pack:

```powershell
python -m bioresearch_agent --skill-pack D:\path\to\skills --list-external-skills
```

Remote GitHub skill pack:

```powershell
python -m bioresearch_agent --skill-pack github:aipoch/medical-research-skills --list-external-skills
python -m bioresearch_agent --skill-pack github:HughYau/AcademicForge --list-external-skills
```

If GitHub rate limits anonymous API calls, set `GITHUB_TOKEN` or `GH_TOKEN`.

## LangGraph Handoff

Generate adapter-neutral node specs:

```powershell
python -m bioresearch_agent --skill-pack github:aipoch/medical-research-skills --langgraph-node-specs --json
```

Each node spec contains:

- `node_id`
- `skill_id`
- trigger summary
- input contract
- output contract
- safety policy

The generated spec is intentionally independent of a concrete LangGraph import path, so it can be consumed by a local graph builder without forcing BioResearch-Agent to vendor external repos.

## Weaver Memory Route

Every end-to-end run emits a Weaver-compatible path pattern:

```text
condition -> action policy -> validation gate -> fallback -> rollback rule
```

The pattern is stored in `memory_trace.path_patterns`. It can be handed to a MemoryWeaver-style harness for promotion, challenge, rollback, or archival after repeated successful runs.

Promotion evidence should come from:

- passing tests;
- benchmark deltas;
- source-provenance checks;
- explicit user correction or approval;
- repeated successful sibling runs;
- rollback records.

Model confidence alone is not promotion evidence.

## Clean-Room Boundary

External projects used as references or skill sources remain outside this repository.

Do not copy:

- external skill prose into reports;
- private PathoFlow code, logs, `.env`, tool manifests, WISH/Pinglab assets, generated reports, or runtime paths;
- copyrighted article prose;
- unverified tool parameters, outputs, or benchmark claims.

PathoFlow is used as a high-level architecture reference for layered contracts, provenance, execution gates, observability, and failure-path handling. It is not used as a code source.

## Current Smoke Results

Verified during development:

| Skill pack | Mode | Result |
| --- | --- | --- |
| `github:aipoch/medical-research-skills` | remote GitHub index | 605 `SKILL.md` entries discovered |
| `github:HughYau/AcademicForge` | remote GitHub index | 15 `SKILL.md` entries discovered |
| `D:\Download\PathoFlow` | local directory | 0 `SKILL.md` entries; used as architecture reference, not a skill pack |
