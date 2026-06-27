# Skill And Tool Extension Design

## Goal

BioResearch-Agent should expand around a narrow reference workflow:

```text
search references -> attach neutral markers -> verify marker support -> compare same-marker papers -> expand search
```

The design goal is:

```text
new capability = new bounded reference skill or registered tool
not = hidden prompt rules or private implementation copies
```

## Skill Interface

| Field | Meaning |
| --- | --- |
| `skill_id` | Stable public-safe name, no private project code name. |
| `purpose` | What the skill helps with. |
| `trigger` | When the agent should consider using it. |
| `inputs` | Required non-sensitive inputs. |
| `outputs` | Structured output format. |
| `evidence_required` | What evidence must support the output. |
| `privacy_boundary` | What the skill must not access or reveal. |
| `human_review` | Whether review is required before use. |

Example:

```yaml
skill_id: reference_mapping
purpose: Search public references, attach neutral markers, verify support, and compare same-marker papers.
trigger: User asks for related work, paper screening, tagging, marker verification, or method comparison.
inputs:
  - query
  - public paper metadata
outputs:
  - candidate references
  - neutral markers
  - marker verification records
  - same-marker comparison table
evidence_required:
  - title
  - abstract
  - publication source
  - visible tags
privacy_boundary:
  - no private patient data
  - no internal project files
human_review: required
```

## Tool Interface

| Tool | Purpose |
| --- | --- |
| `reference_search` | Search public-safe reference metadata. |
| `reference_mark` | Attach neutral markers to references. |
| `marker_verify` | Check whether markers are supported by title/abstract/tags. |
| `marker_compare` | Compare references that share the same marker. |
| `markdown_brief_export` | Export reviewable summaries. |

Each registered tool also declares:

- `required_inputs`: context fields that must exist before the tool can run.
- `produced_outputs`: result fields that are merged into the shared chain context.

`ToolRegistry.run_chain(...)` executes tools in order. Successful outputs become inputs for later tools. A tool with missing required inputs is marked `skipped`; a handler exception or omitted declared output is marked `failed`. Failed outputs are not merged, so dependent tools cannot run on partial handoffs. This keeps handoffs explicit and testable without adding private execution adapters.

## Router Logic

```text
question
  -> classify intent
  -> search references
  -> attach neutral markers
  -> verify marker support
  -> compare same-marker references
  -> require human review for claims
```

## Safety Rules

- Skills do not automatically become tools.
- Tool outputs do not automatically become verified facts.
- LLM-generated text cannot override privacy boundaries.
- Markers are neutral grouping labels, not good/bad judgments.
- Marker verification checks metadata support; it does not prove full-paper correctness.
- High-risk biomedical claims require evidence and human review.
- Private data must be excluded from public demos and documentation.

## Optimization Direction

1. Add public adapters for PubMed/arXiv search.
2. Add citation fields and marker provenance to every research answer.
3. Add review status to marker verification reports.
4. Add same-marker contrast tables for paper groups.
5. Keep all private integrations behind placeholders or omitted entirely.
