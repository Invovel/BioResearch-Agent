# Full Architecture Partition

BioResearch-Agent uses this layered shape:

| Layer | Responsibility |
| --- | --- |
| Framework | Graph state, routing, runtime policy, guardrails. |
| Agent | Planner, research, execution, and workspace roles. |
| Skill | Bounded capability such as discovery, evidence, archive, or execution review. |
| Tool | Catalog entry, safe adapter, or placeholder. |
| Memory | Public/synthetic session, project, and evidence records. |

## Execution Boundary

No tool in this prototype performs production execution. The execution layer is
represented as an adapter interface that returns a blocked placeholder result.

## Future Public Adapter Rule

A placeholder may become callable only after:

1. The adapter has a public implementation.
2. Tests cover expected inputs, outputs, and failure modes.
3. The privacy gate rejects private paths, patient identifiers, credentials, and logs.
4. The README documents the new public-safe behavior.

