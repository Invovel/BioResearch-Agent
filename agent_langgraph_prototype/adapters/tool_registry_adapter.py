"""Local catalog adapter for public-safe tool discovery."""

from __future__ import annotations

from typing import Any


class ToolRegistryAdapter:
    """Expose skill-linked tool ids as catalog-only records."""

    def __init__(self, catalog: dict[str, dict[str, Any]] | None = None):
        self._catalog = catalog or build_catalog_from_skills()

    def manifest_summary(self) -> list[dict[str, Any]]:
        return [
            {
                "tool_id": tool_id,
                "kind": item["kind"],
                "used_by_skills": item["used_by_skills"],
                "execution_mode": "catalog_only_stub",
                "requires_review": True,
            }
            for tool_id, item in sorted(self._catalog.items())
        ]

    def tool_detail(self, tool_id: str) -> dict[str, Any] | None:
        item = self._catalog.get(tool_id)
        if not item:
            return None
        return {
            "tool_id": tool_id,
            "kind": item["kind"],
            "used_by_skills": item["used_by_skills"],
            "description": "Public-safe catalog entry. No private execution implementation is included.",
            "execution_mode": "catalog_only_stub",
            "requires_review": True,
        }

    def tool_io_spec(self, tool_id: str) -> dict[str, Any] | None:
        if tool_id not in self._catalog:
            return None
        return {
            "tool_id": tool_id,
            "inputs": ["public_or_synthetic_metadata"],
            "outputs": ["reviewable_structured_summary"],
            "forbidden": ["private_data", "patient_identifiers", "internal_paths", "model_paths"],
        }

    def tool_compatibility(self, from_tool: str, from_output: str, to_tool: str, to_input: str) -> dict[str, Any]:
        known = from_tool in self._catalog and to_tool in self._catalog
        return {
            "compatible": bool(known and from_output and to_input),
            "status": "catalog_check_only",
            "reason": "Compatibility is not executed; it is a public-safe planning hint.",
        }

    def cpu_tools(self) -> list[dict[str, Any]]:
        return [
            item
            for item in self.manifest_summary()
            if item["kind"] in {"read_only", "service_bundle", "planning"}
        ]


def build_catalog_from_skills() -> dict[str, dict[str, Any]]:
    from agent_langgraph_prototype.skills.registry import SKILLS

    catalog: dict[str, dict[str, Any]] = {}
    for skill_id, skill in SKILLS.items():
        for tool_id in skill.get("tools", ()):
            entry = catalog.setdefault(
                tool_id,
                {
                    "kind": skill.get("kind", "tool"),
                    "used_by_skills": [],
                },
            )
            if skill_id not in entry["used_by_skills"]:
                entry["used_by_skills"].append(skill_id)
    return catalog

