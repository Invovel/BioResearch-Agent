# Vibe Coding Notes

BioResearch-Agent is now organized as a small skill/tool kit, not a large web app or platform plan.

## Keep

- `bioresearch_agent/skills.py`
- `bioresearch_agent/tools.py`
- `bioresearch_agent/privacy.py`
- `bioresearch_agent/retrieval.py`
- `bioresearch_agent/cli.py`
- tests for the public-safe behavior

## Avoid

- Web UI claims.
- Clinical diagnosis claims.
- Long roadmap promises.
- Private project names.
- Internal tool IDs or manifests.
- Real datasets, logs, model paths, deployment paths, or screenshots.

## Working Loop

```text
question
  -> privacy gate
  -> skill selection
  -> optional public-safe tool call
  -> structured answer
  -> human review
```

## Extension Style

Add one capability at a time:

1. Add a `SkillSpec` or `ToolSpec`.
2. Add a small handler.
3. Add one focused test.
4. Keep examples synthetic or public.

