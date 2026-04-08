#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path

from report_validators import (
    ValidationError,
    validate_block_requirements,
    validate_block_rtl_package,
    validate_dv_coverage_plan,
    validate_dv_objectives,
    validate_dv_plan,
    validate_microarchitecture_spec,
    validate_rtl_verification_surface,
    validate_rdc_report,
    validate_rtl_design,
    validate_rtl_lint_report,
    validate_sva_plan,
    validate_uvm_test_plan,
    load_json_like_yaml,
    validate_cdc_report,
    validate_timing_report,
)


ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = ROOT / "evals" / "smoke"


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


def validate_case(metadata_path: Path, errors: list[str]) -> None:
    rel = metadata_path.relative_to(ROOT)
    try:
        metadata = load_json(metadata_path)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid metadata JSON in {rel}: {exc}")
        return

    required_keys = {"eval_name", "skill", "input_files", "expected_output", "schema", "assertions"}
    missing = required_keys - metadata.keys()
    if missing:
        errors.append(f"{rel} is missing keys: {', '.join(sorted(missing))}")
        return

    skill_dir = metadata_path.parent.parent.name
    if metadata["skill"] != skill_dir:
        errors.append(f"{rel} skill mismatch: expected {skill_dir}, got {metadata['skill']}")

    if not isinstance(metadata["input_files"], list) or not metadata["input_files"]:
        errors.append(f"{rel} input_files must be a non-empty list")
        return
    if not isinstance(metadata["assertions"], list) or not metadata["assertions"]:
        errors.append(f"{rel} assertions must be a non-empty list")

    for input_file in metadata["input_files"]:
        input_path = ROOT / input_file
        if not input_path.exists():
            errors.append(f"{rel} references missing input file: {input_file}")

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
        if schema_name == "cdc-report.schema.json":
            validate_cdc_report(expected)
        elif schema_name == "timing-report.schema.json":
            validate_timing_report(expected)
        elif schema_name == "dv-objectives.schema.json":
            validate_dv_objectives(expected)
        elif schema_name == "rtl-verification-surface.schema.json":
            validate_rtl_verification_surface(expected)
        elif schema_name == "uvm-test-plan.schema.json":
            validate_uvm_test_plan(expected)
        elif schema_name == "sva-plan.schema.json":
            validate_sva_plan(expected)
        elif schema_name == "dv-coverage-plan.schema.json":
            validate_dv_coverage_plan(expected)
        elif schema_name == "dv-plan.schema.json":
            validate_dv_plan(expected)
        elif schema_name == "block-requirements.schema.json":
            validate_block_requirements(expected)
        elif schema_name == "microarchitecture-spec.schema.json":
            validate_microarchitecture_spec(expected)
        elif schema_name == "rtl-design.schema.json":
            validate_rtl_design(expected)
        elif schema_name == "rtl-lint-report.schema.json":
            validate_rtl_lint_report(expected)
        elif schema_name == "rdc-report.schema.json":
            validate_rdc_report(expected)
        elif schema_name == "block-rtl-package.schema.json":
            validate_block_rtl_package(expected)
        else:
            errors.append(f"{rel} references unsupported schema for local validation: {schema_name}")
    except ValidationError as exc:
        errors.append(f"{expected_path.relative_to(ROOT)} failed validation: {exc}")


def main() -> int:
    errors: list[str] = []
    metadata_files = sorted(EVALS_DIR.glob("*/*/metadata.json"))
    if not metadata_files:
        errors.append("no smoke eval metadata files found under evals/smoke/")

    for metadata_path in metadata_files:
        validate_case(metadata_path, errors)

    if errors:
        print("smoke eval validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"smoke eval validation passed for {len(metadata_files)} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
