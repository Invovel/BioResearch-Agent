from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
import urllib.request
from http.client import IncompleteRead
from urllib.error import HTTPError, URLError
from pathlib import Path

from .schemas import ExternalSkillSpec, LangGraphNodeSpec


SKILL_FILE_NAME = "SKILL.md"
SKIP_DIR_NAMES = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    "data",
    "logs",
    "exports",
    "reports",
    "backups",
    "vendor",
    "node_modules",
}


def discover_external_skills(root: str | Path, *, source: str = "local") -> tuple[ExternalSkillSpec, ...]:
    """Discover Codex/Claude-style SKILL.md files without copying their contents."""

    root_text = str(root)
    github_ref = _parse_github_ref(root_text)
    if github_ref:
        return discover_github_skills(*github_ref)

    root_path = Path(root).expanduser().resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"Skill pack root does not exist: {root_path}")
    specs: list[ExternalSkillSpec] = []
    for skill_file in _iter_skill_files(root_path):
        text = skill_file.read_text(encoding="utf-8", errors="replace")
        spec = _parse_skill_file(skill_file, text, source=source, root=root_path)
        specs.append(spec)
    specs.sort(key=lambda item: item.skill_id)
    return tuple(specs)


def discover_github_skills(owner: str, repo: str, branch: str = "") -> tuple[ExternalSkillSpec, ...]:
    """Discover remote GitHub SKILL.md files directly through the public API."""

    if not branch:
        metadata = _get_json(f"https://api.github.com/repos/{owner}/{repo}")
        branch = str(metadata.get("default_branch") or "main")
    tree = _get_json(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{urllib.parse.quote(branch, safe='')}?recursive=1")
    specs: list[ExternalSkillSpec] = []
    for item in tree.get("tree", []):
        path = str(item.get("path", ""))
        if not path.endswith(SKILL_FILE_NAME):
            continue
        if set(Path(path).parts[:-1]) & SKIP_DIR_NAMES:
            continue
        spec = _remote_skill_from_path(
            path=path,
            source=f"github:{owner}/{repo}@{branch}",
        )
        specs.append(spec)
    specs.sort(key=lambda item: item.skill_id)
    return tuple(specs)


def recommend_external_skills(query: str, specs: tuple[ExternalSkillSpec, ...], *, limit: int = 8) -> tuple[ExternalSkillSpec, ...]:
    """Rank discovered external skills by simple transparent lexical overlap."""

    query_terms = _tokens(query)
    ranked = []
    for spec in specs:
        haystack = _tokens(" ".join([spec.skill_id, spec.name, spec.description, " ".join(spec.tags)]))
        overlap = len(query_terms & haystack)
        if overlap:
            ranked.append((overlap, spec))
    ranked.sort(key=lambda item: (-item[0], item[1].skill_id))
    return tuple(spec for _, spec in ranked[:limit])


def build_langgraph_node_specs(specs: tuple[ExternalSkillSpec, ...]) -> tuple[LangGraphNodeSpec, ...]:
    """Create adapter-neutral LangGraph node contracts for external skills."""

    nodes = []
    for spec in specs:
        nodes.append(
            LangGraphNodeSpec(
                node_id=f"external_skill::{spec.skill_id}",
                skill_id=spec.skill_id,
                trigger_summary=spec.description or spec.name,
                input_contract=(
                    "public_safe_research_question",
                    "retrieved_public_evidence_or_manuscript_context",
                    "human_review_boundary",
                ),
                output_contract=(
                    "skill_scaffold_or_audit",
                    "evidence_requirements",
                    "unsupported_claims_or_follow_up_tasks",
                ),
                safety_policy=(
                    "Do not execute external skill scripts by default.",
                    "Do not copy external skill prose into generated reports.",
                    "Treat SKILL.md as routing and operating guidance; keep evidence claims source-backed.",
                    "Record successful and failed routes into MemoryWeaver-compatible path patterns.",
                ),
            )
        )
    return tuple(nodes)


def render_external_skill_index(specs: tuple[ExternalSkillSpec, ...], *, query: str = "") -> str:
    selected = recommend_external_skills(query, specs) if query else specs
    lines = [
        "# External Skill Pack Index",
        "",
        f"- Discovered skills: {len(specs)}",
        f"- Displayed skills: {len(selected)}",
        "",
        "| Skill | Description | Path |",
        "| --- | --- | --- |",
    ]
    for spec in selected:
        lines.append(f"| `{spec.skill_id}` | {_cell(spec.description or spec.name)} | `{spec.path}` |")
    return "\n".join(lines) + "\n"


def _iter_skill_files(root: Path):
    for path in root.rglob(SKILL_FILE_NAME):
        parts = set(path.relative_to(root).parts[:-1])
        if parts & SKIP_DIR_NAMES:
            continue
        yield path


def _parse_skill_file(path: Path, text: str, *, source: str, root: Path) -> ExternalSkillSpec:
    frontmatter = _frontmatter(text)
    name = frontmatter.get("name") or _first_heading(text) or path.parent.name
    description = frontmatter.get("description") or _first_paragraph(text)
    rel_path = path.relative_to(root).as_posix()
    skill_id = _safe_id(name or path.parent.name)
    tags = tuple(sorted(set(_tokens(" ".join([skill_id, description])) & {"academic", "writing", "medical", "research", "audit", "citation", "review", "protocol"})))
    return ExternalSkillSpec(
        skill_id=skill_id,
        name=name.strip(),
        description=_clean(description),
        path=rel_path,
        source=source,
        tags=tags,
    )


def _remote_skill_from_path(*, path: str, source: str) -> ExternalSkillSpec:
    name = Path(path).parent.name
    category = Path(path).parent.parent.name if len(Path(path).parts) > 2 else ""
    description = f"Remote SKILL.md discovered from {source}"
    if category:
        description = f"{category} skill. {description}"
    skill_id = _safe_id(name or Path(path).parent.name)
    tags = tuple(sorted(set(_tokens(" ".join([skill_id, description])) & {"academic", "writing", "medical", "research", "audit", "citation", "review", "protocol"})))
    return ExternalSkillSpec(
        skill_id=skill_id,
        name=name.strip(),
        description=_clean(description),
        path=path,
        source=source,
        tags=tags,
    )


def _parse_github_ref(value: str) -> tuple[str, str, str] | None:
    value = value.strip()
    branch = ""
    if value.startswith("github:"):
        payload = value.removeprefix("github:")
    elif value.startswith("https://github.com/"):
        payload = value.removeprefix("https://github.com/")
    else:
        return None
    if "@" in payload:
        payload, branch = payload.rsplit("@", 1)
    parts = payload.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub skill pack reference: {value}")
    return parts[0], parts[1], branch


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    payload = text[3:end]
    result: dict[str, str] = {}
    current_key = ""
    for line in payload.splitlines():
        if not line.strip():
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:", line):
            key, value = line.split(":", 1)
            current_key = key.strip()
            result[current_key] = value.strip().strip("\"'")
        elif current_key:
            result[current_key] = _clean(" ".join([result[current_key], line.strip().strip("\"'")]))
    return result


def _first_heading(text: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _first_paragraph(text: str) -> str:
    cleaned = re.sub(r"^---.*?---", "", text, flags=re.DOTALL).strip()
    for block in re.split(r"\n\s*\n", cleaned):
        block = block.strip()
        if block and not block.startswith("#"):
            return block
    return ""


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_+-]{2,}", text.lower()))


def _safe_id(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "external-skill"


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _cell(text: str) -> str:
    return _clean(text).replace("|", "\\|")


def _get_json(url: str) -> dict:
    return json.loads(_get_text(url))


def _get_text(url: str) -> str:
    headers = {"User-Agent": "BioResearch-Agent external skill discovery"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and "github" in urllib.parse.urlparse(url).netloc:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return response.read().decode("utf-8", errors="replace")
        except IncompleteRead as exc:
            last_error = exc
            time.sleep(1.0 + attempt)
        except HTTPError as exc:
            if exc.code in {403, 429} and "api.github.com" in url:
                raise RuntimeError(
                    "GitHub API rate limit while discovering remote skills. "
                    "Set GITHUB_TOKEN or GH_TOKEN, or use a local clone as --skill-pack."
                ) from exc
            raise
        except URLError as exc:
            last_error = exc
            time.sleep(1.0 + attempt)
    raise RuntimeError(f"Network read failed while discovering remote skills: {url}") from last_error
