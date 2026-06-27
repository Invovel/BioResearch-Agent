"""LLM routing helpers for skill/tool selection."""

from __future__ import annotations

from .models import LLM_MODELS
from .skill_tool_map import LLM_SKILL_TOOL_MAP


def get_skills_for_llm(llm_name: str) -> list[str]:
    entry = LLM_MODELS.get(llm_name) or {}
    return list(entry.get("preferred_skills") or [])


def get_tools_for_skill(llm_name: str, skill_name: str) -> list[str]:
    mapping = LLM_SKILL_TOOL_MAP.get(llm_name) or {}
    skills = mapping.get("skills") or {}
    return list(skills.get(skill_name) or [])


def describe_llm_routing(llm_name: str) -> dict:
    model = LLM_MODELS.get(llm_name) or {}
    skills = get_skills_for_llm(llm_name)
    return {
        "llm": llm_name,
        "role": model.get("role", ""),
        "description": model.get("description", ""),
        "skills": {
            skill: get_tools_for_skill(llm_name, skill)
            for skill in skills
        },
    }


