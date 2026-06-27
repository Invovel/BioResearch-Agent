# Framework-First Partition

The prototype starts from framework boundaries before adding agent behavior.

## Principle

```text
framework -> agent -> skill -> tool
```

- Framework owns state, routing, runtime policy, and guardrails.
- Agent owns role-level planning.
- Skill owns a bounded capability.
- Tool owns one callable or placeholder action.

## Why This Matters

Putting framework first prevents tool execution from becoming a hidden side
effect of a chat response. Privileged actions must pass through explicit
contracts, review gates, and adapter boundaries.

## Current State

- Local graph routing is available.
- Skill/tool mappings are catalog-only.
- Execution adapters are placeholders.
- Private runtimes and copied implementation code are intentionally excluded.

