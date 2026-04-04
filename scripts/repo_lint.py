#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
EXPECTED_TOP_LEVEL = [
    "README.md",
    "AGENTS.md",
    "skills",
    "rules",
    "flows",
]


def is_external_link(target: str) -> bool:
    return (
        target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("mailto:")
        or target.startswith("#")
    )


def check_expected_paths(errors: list[str]) -> None:
    for rel in EXPECTED_TOP_LEVEL:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing expected top-level path: {rel}")


def check_empty_readmes(errors: list[str]) -> None:
    for path in ROOT.rglob("README.md"):
        if path.stat().st_size == 0:
            errors.append(f"empty README.md: {path.relative_to(ROOT)}")


def check_json_files(errors: list[str]) -> None:
    for path in ROOT.rglob("*.json"):
        if ".git" in path.parts:
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            rel = path.relative_to(ROOT)
            errors.append(f"invalid JSON in {rel}: {exc}")


def check_markdown_links(errors: list[str]) -> None:
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            target = target.strip()
            if not target or is_external_link(target):
                continue
            clean_target = target.split("#", 1)[0]
            if not clean_target:
                continue
            if clean_target.startswith("/"):
                continue
            resolved = (path.parent / clean_target).resolve()
            if not resolved.exists():
                rel = path.relative_to(ROOT)
                errors.append(f"broken local markdown link in {rel}: {target}")


def main() -> int:
    errors: list[str] = []
    check_expected_paths(errors)
    check_empty_readmes(errors)
    check_json_files(errors)
    check_markdown_links(errors)

    if errors:
        print("repo lint failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("repo lint passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
