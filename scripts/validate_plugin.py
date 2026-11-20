#!/usr/bin/env python3
"""Cross-platform validator for the sdlc-master-orchestrator Antigravity plugin.

Runs both locally and in GitHub Actions CI without requiring the `agy` binary.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
MANIFEST_PATH = REPO_ROOT / "plugin.json"

MAX_SKILL_BODY_BYTES = 24_000
MAX_SKILL_NAME_LEN = 64
MAX_SKILL_DESC_LEN = 1024

KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LOGO_REL_PATH_RE = re.compile(
    r"^(?![A-Za-z][A-Za-z0-9+.-]*:)(?!/)(\S.*)\.(png|svg|jpg|jpeg|webp)$",
    re.IGNORECASE,
)
LOGO_ALLOWLIST_URL_RE = re.compile(
    r"^https://([A-Za-z0-9-]+\.)*(google\.com|gstatic\.com|googleusercontent\.com)(:[0-9]+)?([/?#].*)?$"
)

# Official keys from https://antigravity.google/schemas/v1/plugin.json
ALLOWED_MANIFEST_KEYS = frozenset(
    {
        "$schema",
        "name",
        "displayName",
        "display_name",
        "description",
        "version",
        "disabled",
        "logo",
        "suggestedPrompts",
        "suggested_prompts",
        "skills",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "extensions",
    }
)

FORBIDDEN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("macOS user home path", re.compile(r"/Users/")),
    ("Linux user home path", re.compile(r"/home/[a-zA-Z0-9._-]+/")),
    ("Hardcoded file:// path", re.compile(r"file:///(?:Users|home)/")),
    ("Internal google3 reference", re.compile(r"\bgoogle3\b|\bpyformat\b")),
    ("API key / token pattern", re.compile(r"\b(?:AIza[0-9A-Za-z_-]{35}|ghp_[A-Za-z0-9]{36})\b")),
]

# Optional extra colon-separated regexes via PLUGIN_EXTRA_FORBIDDEN_PATTERNS
if extra_pat := os.environ.get("PLUGIN_EXTRA_FORBIDDEN_PATTERNS", "").strip():
    for idx, raw_pat in enumerate(extra_pat.split("::"), start=1):
        if raw_pat.strip():
            FORBIDDEN_PATTERNS.append((f"Custom pattern #{idx}", re.compile(raw_pat.strip(), re.IGNORECASE)))

# Matches markdown links: [label](target)
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def validate_manifest(errors: list[str]) -> None:
    """Validates plugin.json against Antigravity v1 manifest schema rules."""
    if not MANIFEST_PATH.is_file():
        errors.append(f"Missing manifest: {MANIFEST_PATH}")
        return
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in plugin.json: {exc}")
        return

    if not isinstance(data, dict):
        errors.append("plugin.json root must be a JSON object")
        return

    unknown_keys = sorted(set(data.keys()) - ALLOWED_MANIFEST_KEYS)
    if unknown_keys:
        errors.append(f"plugin.json contains unsupported top-level keys: {unknown_keys}")

    for field in ("name", "displayName", "version", "description", "license"):
        val = data.get(field)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"plugin.json missing required non-empty string field: {field!r}")

    name = data.get("name", "")
    if isinstance(name, str) and name and not KEBAB_CASE_RE.match(name):
        errors.append(f"plugin.json.name {name!r} must be lowercase kebab-case")

    repo = data.get("repository")
    if repo is not None and (not isinstance(repo, str) or not repo.strip()):
        errors.append("plugin.json.repository must be a non-empty URL string (per Antigravity v1 schema)")

    homepage = data.get("homepage")
    if homepage is not None and (not isinstance(homepage, str) or not homepage.startswith("https://")):
        errors.append("plugin.json.homepage must be an https:// URL string")

    prompts = data.get("suggestedPrompts")
    if prompts is not None:
        if (
            not isinstance(prompts, list)
            or len(prompts) > 3
            or any(not isinstance(p, str) or not p.strip() for p in prompts)
        ):
            errors.append("plugin.json.suggestedPrompts must be a list of <= 3 non-empty strings")

    logo = data.get("logo")
    if logo is not None:
        if not isinstance(logo, str):
            errors.append("plugin.json.logo must be a string")
        elif LOGO_REL_PATH_RE.match(logo):
            logo_path = (REPO_ROOT / logo).resolve()
            if not logo_path.is_file():
                errors.append(f"plugin.json.logo file does not exist: {logo!r}")
        elif not LOGO_ALLOWLIST_URL_RE.match(logo):
            errors.append(f"plugin.json.logo must be a relative asset path or allowlisted Google URL: {logo!r}")


def parse_frontmatter(text: str) -> tuple[dict[str, object], str] | None:
    """Extracts YAML frontmatter (including folded/literal blocks) and body text."""
    if not text.startswith("---\n"):
        return None
    end_idx = text.find("\n---\n", 4)
    if end_idx == -1:
        return None
    fm_block = text[4:end_idx]
    body = text[end_idx + 5 :]

    fields: dict[str, object] = {}
    lines = fm_block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if ":" in line and not line.startswith((" ", "\t")):
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val in (">-", ">", "|-", "|"):
                block_lines: list[str] = []
                i += 1
                while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                    stripped = lines[i].strip()
                    if stripped:
                        block_lines.append(stripped)
                    i += 1
                joiner = " " if val.startswith(">") else "\n"
                fields[key] = joiner.join(block_lines)
                continue
            if val == "":
                nested: dict[str, str] = {}
                i += 1
                while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                    stripped = lines[i].strip()
                    if ":" in stripped:
                        sk, sv = stripped.split(":", 1)
                        nested[sk.strip()] = sv.strip().strip("'\"")
                    i += 1
                fields[key] = nested
                continue
            fields[key] = val.strip("'\"")
        i += 1

    return fields, body


def check_markdown_files(md_files: list[pathlib.Path], errors: list[str]) -> None:
    """Checks markdown files for forbidden patterns and broken relative links."""
    for md_file in md_files:
        rel_md = md_file.relative_to(REPO_ROOT)
        text = md_file.read_text(encoding="utf-8")
        is_third_party_styleguide = md_file.name == "style_guide_full.md"

        for label, pattern in FORBIDDEN_PATTERNS:
            if is_third_party_styleguide and "google3" in label:
                continue
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{rel_md}:{line_no}: forbidden pattern ({label}): {match.group(0)!r}"
                )

        if is_third_party_styleguide:
            continue

        in_fence = False
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for match in MD_LINK_RE.finditer(line):
                target = match.group(1).strip()
                if target.startswith(("http://", "https://", "mailto:", "#", "file://")):
                    continue
                target_path_str = target.split("#", 1)[0]
                if not target_path_str:
                    continue
                resolved = (md_file.parent / target_path_str).resolve()
                if not resolved.exists():
                    errors.append(
                        f"{rel_md}:{line_no}: broken relative link {target!r} "
                        f"(resolved to {resolved})"
                    )


def validate_skills(errors: list[str]) -> int:
    """Validates all skills under skills/."""
    if not SKILLS_DIR.is_dir():
        errors.append(f"Missing skills directory: {SKILLS_DIR}")
        return 0

    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    if not skill_dirs:
        errors.append("No skill directories found under skills/")
        return 0

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"Missing SKILL.md in {skill_dir.relative_to(REPO_ROOT)}")
            continue

        raw = skill_md.read_text(encoding="utf-8")
        parsed = parse_frontmatter(raw)
        if parsed is None:
            errors.append(f"{skill_md.relative_to(REPO_ROOT)}: missing valid YAML frontmatter")
            continue

        fields, body = parsed
        name = str(fields.get("name", ""))
        if name != skill_dir.name:
            errors.append(
                f"{skill_md.relative_to(REPO_ROOT)}: frontmatter name {name!r} "
                f"does not match directory name {skill_dir.name!r}"
            )
        if not KEBAB_CASE_RE.match(name) or len(name) > MAX_SKILL_NAME_LEN:
            errors.append(
                f"{skill_md.relative_to(REPO_ROOT)}: skill name {name!r} "
                f"must be kebab-case and <= {MAX_SKILL_NAME_LEN} chars"
            )

        desc = fields.get("description")
        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"{skill_md.relative_to(REPO_ROOT)}: missing non-empty frontmatter 'description'")
        elif len(desc) > MAX_SKILL_DESC_LEN:
            errors.append(
                f"{skill_md.relative_to(REPO_ROOT)}: description is {len(desc)} chars "
                f"(exceeds {MAX_SKILL_DESC_LEN}-char Antigravity limit)"
            )

        body_bytes = len(body.encode("utf-8"))
        if body_bytes > MAX_SKILL_BODY_BYTES:
            errors.append(
                f"{skill_md.relative_to(REPO_ROOT)}: body is {body_bytes} bytes "
                f"(exceeds {MAX_SKILL_BODY_BYTES}-byte Antigravity cap)"
            )

    md_files = sorted(SKILLS_DIR.rglob("*.md"))
    for doc_name in ("README.md", "CONTRIBUTING.md"):
        doc_path = REPO_ROOT / doc_name
        if doc_path.is_file():
            md_files.append(doc_path)
    check_markdown_files(md_files, errors)

    return len(skill_dirs)


def main() -> int:
    errors: list[str] = []
    validate_manifest(errors)
    skill_count = validate_skills(errors)

    if errors:
        print(f"VALIDATION FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"VALIDATION PASSED: plugin.json valid, {skill_count} skills verified, 0 errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
