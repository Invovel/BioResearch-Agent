# BioResearch-Agent LangGraph Prototype

This directory is a clean-room prototype for experimenting with:

- `framework -> agent -> skill -> tool` decomposition.
- Local graph routing and optional LangGraph-style execution.
- Skill-to-tool catalog design.
- Review gates around privileged execution.

It does **not** include private platform source, private data, production
execution bridges, model paths, deployment paths, or full internal tool
manifests. Every adapter is a local stub until a public implementation is
written.

## Directory Contract

| Path | Purpose |
| --- | --- |
| `framework/` | Graph, router, state, and runtime boundaries. |
| `agents/` | Agent role facades. |
| `skills/` | Skill definitions and skill-to-tool mappings. |
| `adapters/` | Public-safe stubs for discovery, flow planning, papers, execution, and archive. |
| `contracts/` | Graph state and skill request/response contracts. |
| `memory/` | Session/project/evidence memory boundary notes. |
| `guardrails/` | Execution, interpretation, and privilege gate concepts. |
| `docs/` | Internal notes for this prototype. |

## Current Safety Shape

```text
query
  -> local graph route
  -> agent role
  -> skill
  -> catalog-only tool adapter
  -> reviewable output
```

Privileged actions are blocked by default. `ExecutionAdapter.execute_tool()`
returns `blocked_placeholder` rather than executing external tools.

## Entrypoints

```powershell
python agent_langgraph_prototype\run_demo.py
```

Supported `PrototypeOrchestrator.run()` modes:

- `tool_manifest`
- `tool_detail`
- `tool_io_spec`
- `tool_compatibility`
- `flow_plan`
- `paper_search`
- `paper_stats`
- `paper_analyze`
- `paper_toolchain`
- `prepare_query`
- `prepare_flow_plan`
- `execute_tool`
- `inspect_manifest`
- `locate_result_file`
- `archive_session`
- `get_session_record`

All modes are local planning/stub modes unless explicitly replaced by future
public adapters.

## Development Rules

- Keep this directory self-contained.
- Do not import private external packages.
- Do not commit full private manifests, logs, caches, datasets, model paths, or credentials.
- Preserve skill/tool flow order as a catalog, not as copied execution code.
- Add tests before upgrading any placeholder into a callable adapter.

