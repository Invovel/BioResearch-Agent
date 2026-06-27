# AGENTS.md

Use `CODEX.md` as the primary agent operating guide for this repository.

Short version:

- This is a public-safe personal biomedical research-agent project.
- Keep all work inside the clean BioResearch-Agent boundary.
- Do not copy private implementation code, data, logs, internal paths, API routes, model paths, or credentials from external projects.
- Skills should remain bounded and reviewable.
- Tools should be safe adapters, stubs, or placeholders unless a clean public implementation exists.
- Run `python -m pytest -q` before reporting code changes.

Recommended reading order:

1. `README.md`
2. `SKILL.md`
3. `CODEX.md`
4. `docs/privacy_sanitization.md`
5. `docs/skills_tools_extension.md`
6. `tests/test_agent.py`

Default validation:

```powershell
python -m pytest -q
python -m bioresearch_agent --list-skills
python -m bioresearch_agent --list-tools
```
