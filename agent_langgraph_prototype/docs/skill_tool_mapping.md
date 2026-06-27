# Skill To Tool Mapping

## Principle

- A skill is a bounded capability.
- A tool is a catalog entry, adapter, or placeholder action.
- Agents call skills; skills expose tool candidates.
- Approval, authentication, quota, scheduling, and execution gates belong to the framework layer.

## Current Skills

The canonical ordered mapping lives in:

```text
skills/registry.py
```

The registry intentionally keeps:

- skill name
- function summary
- kind
- ordered tool ids
- clean-room provenance

The registry intentionally excludes:

- private implementation code
- private parameters
- private model paths
- private data paths
- production API routes
- execution traces

## Execution Policy

Every imported or reconstructed tool id is catalog-only unless a future public
adapter explicitly implements it and tests prove the privacy boundary.

