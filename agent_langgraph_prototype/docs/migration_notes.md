# Migration Notes

This directory was sanitized into a clean BioResearch-Agent prototype.

## Kept

- Framework/agent/skill/tool decomposition.
- Skill names and high-level capability order.
- Local graph routing idea.
- Adapter boundary pattern.

## Removed

- Vendored private implementation code.
- Full private tool manifests.
- Real execution bridges.
- Private runtime paths.
- Private API routes, datasets, logs, model paths, and caches.

## Current Mode

All adapters are local stubs until public implementations are added.

