#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def check_json_files(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON in {rel}: {exc}")


def check_yaml_files(errors: list[str]) -> None:
    for suffix in ("*.yaml", "*.yml"):
        for path in sorted(ROOT.rglob(suffix)):
            if ".git" in path.parts:
                continue
            rel = path.relative_to(ROOT)
            text = path.read_text(encoding="utf-8")
            if not text.strip():
                errors.append(f"empty YAML file: {rel}")
                continue
            try:
                list(yaml.safe_load_all(text))
            except yaml.YAMLError as exc:
                errors.append(f"invalid YAML in {rel}: {exc}")


def main() -> int:
    errors: list[str] = []
    check_json_files(errors)
    check_yaml_files(errors)

    if errors:
        print("structured file check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("structured file check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
