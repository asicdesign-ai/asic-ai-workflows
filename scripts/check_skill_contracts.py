#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
RULE_REF_RE = re.compile(r"`(\.\./\.\./rules/[^`]+\.md)`")
YAML_FENCE_RE = re.compile(r"```yaml\s+(.+?)```", re.DOTALL)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---\n"):
        return None, text
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return None, text
    _, remainder = parts
    frontmatter = text[len("---\n") : len(text) - len(remainder) - len("\n---\n")]
    return frontmatter, remainder


def check_frontmatter(skill_path: Path, frontmatter: str | None, errors: list[str]) -> None:
    rel = skill_path.relative_to(ROOT)
    if frontmatter is None:
        errors.append(f"{rel} is missing frontmatter")
        return
    if not re.search(r"^name:\s*[a-z0-9-]+\s*$", frontmatter, re.MULTILINE):
        errors.append(f"{rel} frontmatter is missing a slug-style name")
    if "description:" not in frontmatter:
        errors.append(f"{rel} frontmatter is missing description")


def check_rule_references(skill_path: Path, body: str, errors: list[str]) -> None:
    rel = skill_path.relative_to(ROOT)
    refs = RULE_REF_RE.findall(body)
    if not refs:
        errors.append(f"{rel} does not reference any rules")
        return
    for ref in refs:
        target = (skill_path.parent / ref).resolve()
        if not target.exists():
            errors.append(f"{rel} references missing rule: {ref}")


def check_output_example(skill_path: Path, body: str, errors: list[str]) -> None:
    rel = skill_path.relative_to(ROOT)
    blocks = YAML_FENCE_RE.findall(body)
    if not blocks:
        errors.append(f"{rel} is missing a fenced yaml example block")


def check_h1(skill_path: Path, body: str, errors: list[str]) -> None:
    rel = skill_path.relative_to(ROOT)
    if not re.search(r"^#\s+\S", body, re.MULTILINE):
        errors.append(f"{rel} is missing an H1 heading")


def check_default_config(errors: list[str]) -> None:
    config_path = SKILLS_DIR / "rtl-timing-analyzer" / "default_config.yaml"
    rel = config_path.relative_to(ROOT)
    if not config_path.exists():
        errors.append(f"missing timing default config: {rel}")
        return
    text = read_text(config_path)
    for key in ("depth_thresholds:", "gate_depth_model:", "report:"):
        if key not in text:
            errors.append(f"{rel} is missing top-level key: {key[:-1]}")


def main() -> int:
    errors: list[str] = []
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    if not skill_files:
        errors.append("no skill files found under skills/")

    for skill_path in skill_files:
        text = read_text(skill_path)
        frontmatter, body = split_frontmatter(text)
        check_frontmatter(skill_path, frontmatter, errors)
        check_h1(skill_path, body, errors)
        check_rule_references(skill_path, body, errors)
        check_output_example(skill_path, body, errors)

    check_default_config(errors)

    if errors:
        print("skill contract check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"skill contract check passed for {len(skill_files)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
