#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path

from report_validators import (
    ValidationError,
    load_json_like_yaml,
    validate_pre_synthesis_timing_risk,
)


ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = ROOT / "evals" / "smoke-flows"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_schema_file(path: Path, errors: list[str]) -> None:
    rel = path.relative_to(ROOT)
    try:
        data = load_json(path)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid schema JSON in {rel}: {exc}")
        return
    if not isinstance(data, dict):
        errors.append(f"schema {rel} must be a JSON object")
        return
    for key in ("$schema", "title", "type"):
        if key not in data:
            errors.append(f"schema {rel} is missing key: {key}")


def validate_intermediate_outputs(metadata: dict, rel: Path, errors: list[str]) -> None:
    outputs = metadata.get("intermediate_outputs", [])
    if not isinstance(outputs, list):
        errors.append(f"{rel} intermediate_outputs must be a list")
        return
    for index, item in enumerate(outputs, start=1):
        context = f"{rel} intermediate_outputs[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{context} must be an object")
            continue
        missing = {"name", "path", "schema"} - item.keys()
        if missing:
            errors.append(f"{context} is missing keys: {', '.join(sorted(missing))}")
            continue
        output_path = ROOT / item["path"]
        schema_path = ROOT / item["schema"]
        if not output_path.exists():
            errors.append(f"{context} references missing path: {item['path']}")
        if not schema_path.exists():
            errors.append(f"{context} references missing schema: {item['schema']}")


def validate_case(metadata_path: Path, errors: list[str]) -> None:
    rel = metadata_path.relative_to(ROOT)
    try:
        metadata = load_json(metadata_path)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid metadata JSON in {rel}: {exc}")
        return

    required_keys = {
        "eval_name",
        "flow",
        "input_files",
        "intermediate_outputs",
        "expected_output",
        "schema",
        "assertions",
    }
    missing = required_keys - metadata.keys()
    if missing:
        errors.append(f"{rel} is missing keys: {', '.join(sorted(missing))}")
        return

    flow_dir = metadata_path.parent.parent.name
    if metadata["flow"] != flow_dir:
        errors.append(f"{rel} flow mismatch: expected {flow_dir}, got {metadata['flow']}")

    if not isinstance(metadata["input_files"], list) or not metadata["input_files"]:
        errors.append(f"{rel} input_files must be a non-empty list")
        return
    if not isinstance(metadata["assertions"], list) or not metadata["assertions"]:
        errors.append(f"{rel} assertions must be a non-empty list")

    for input_file in metadata["input_files"]:
        input_path = ROOT / input_file
        if not input_path.exists():
            errors.append(f"{rel} references missing input file: {input_file}")

    validate_intermediate_outputs(metadata, rel, errors)

    schema_path = ROOT / metadata["schema"]
    expected_path = ROOT / metadata["expected_output"]
    if not schema_path.exists():
        errors.append(f"{rel} references missing schema: {metadata['schema']}")
        return
    if not expected_path.exists():
        errors.append(f"{rel} references missing expected output: {metadata['expected_output']}")
        return

    validate_schema_file(schema_path, errors)

    try:
        expected = load_json_like_yaml(expected_path)
    except ValidationError as exc:
        errors.append(str(exc))
        return

    schema_name = schema_path.name
    try:
        if schema_name == "pre-synthesis-timing-risk.schema.json":
            validate_pre_synthesis_timing_risk(expected)
        else:
            errors.append(f"{rel} references unsupported flow schema: {schema_name}")
    except ValidationError as exc:
        errors.append(f"{expected_path.relative_to(ROOT)} failed validation: {exc}")


def main() -> int:
    errors: list[str] = []
    metadata_files = sorted(EVALS_DIR.glob("*/*/metadata.json"))
    if not metadata_files:
        errors.append("no flow smoke metadata files found under evals/smoke-flows/")

    for metadata_path in metadata_files:
        validate_case(metadata_path, errors)

    if errors:
        print("flow smoke validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"flow smoke validation passed for {len(metadata_files)} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
