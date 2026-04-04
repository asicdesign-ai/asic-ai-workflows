#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLOWS_DIR = ROOT / "flows"
RULE_REF_RE = re.compile(r"`(\.\./\.\./rules/[^`]+\.md)`")
SKILL_REF_RE = re.compile(r"`(\.\./\.\./skills/[^`]+/SKILL\.md)`")
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


def check_frontmatter(flow_path: Path, frontmatter: str | None, errors: list[str]) -> None:
    rel = flow_path.relative_to(ROOT)
    if frontmatter is None:
        errors.append(f"{rel} is missing frontmatter")
        return
    if not re.search(r"^name:\s*[a-z0-9-]+\s*$", frontmatter, re.MULTILINE):
        errors.append(f"{rel} frontmatter is missing a slug-style name")
    if "description:" not in frontmatter:
        errors.append(f"{rel} frontmatter is missing description")


def check_references(flow_path: Path, body: str, errors: list[str]) -> None:
    rel = flow_path.relative_to(ROOT)

    rule_refs = RULE_REF_RE.findall(body)
    if not rule_refs:
        errors.append(f"{rel} does not reference any rules")
    for ref in rule_refs:
        target = (flow_path.parent / ref).resolve()
        if not target.exists():
            errors.append(f"{rel} references missing rule: {ref}")

    skill_refs = SKILL_REF_RE.findall(body)
    if not skill_refs:
        errors.append(f"{rel} does not reference any skills")
    for ref in skill_refs:
        target = (flow_path.parent / ref).resolve()
        if not target.exists():
            errors.append(f"{rel} references missing skill: {ref}")


def check_output_example(flow_path: Path, body: str, errors: list[str]) -> None:
    rel = flow_path.relative_to(ROOT)
    blocks = YAML_FENCE_RE.findall(body)
    if not blocks:
        errors.append(f"{rel} is missing a fenced yaml example block")


def check_h1(flow_path: Path, body: str, errors: list[str]) -> None:
    rel = flow_path.relative_to(ROOT)
    if not re.search(r"^#\s+\S", body, re.MULTILINE):
        errors.append(f"{rel} is missing an H1 heading")


def main() -> int:
    errors: list[str] = []
    flow_files = sorted(FLOWS_DIR.glob("*/FLOW.md"))
    if not flow_files:
        errors.append("no flow files found under flows/")

    for flow_path in flow_files:
        text = read_text(flow_path)
        frontmatter, body = split_frontmatter(text)
        check_frontmatter(flow_path, frontmatter, errors)
        check_h1(flow_path, body, errors)
        check_references(flow_path, body, errors)
        check_output_example(flow_path, body, errors)

    if errors:
        print("flow contract check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"flow contract check passed for {len(flow_files)} flows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
