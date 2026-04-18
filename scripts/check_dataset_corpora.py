#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CORPORA_DIR = ROOT / "datasets" / "corpora"
SCHEMAS_DIR = ROOT / "schemas" / "dataset"
SPLIT_NAMES = ("train", "validation", "test")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{rel(path)} must contain one YAML object")
    return data


def require_keys(container: dict, keys: list[str], *, label: str, errors: list[str]) -> None:
    missing = [key for key in keys if key not in container]
    if missing:
        errors.append(f"{label} is missing keys: {', '.join(missing)}")


def validate_evidence_spans(
    evidence: list[dict],
    *,
    label: str,
    compile_files: set[str],
    line_cache: dict[str, list[str]],
    errors: list[str],
) -> None:
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{label} must have at least one evidence span")
        return

    for span in evidence:
        if not isinstance(span, dict):
            errors.append(f"{label} has non-object evidence span")
            continue

        require_keys(span, ["file", "line_start", "line_end"], label=label, errors=errors)
        evidence_file = span.get("file")
        line_start = span.get("line_start")
        line_end = span.get("line_end")

        if not isinstance(evidence_file, str):
            errors.append(f"{label} evidence file must be a string")
            continue
        if not isinstance(line_start, int) or not isinstance(line_end, int):
            errors.append(f"{label} evidence lines must be integers")
            continue
        if line_start < 1 or line_end < line_start:
            errors.append(f"{label} has invalid evidence line range {line_start}-{line_end}")
            continue
        if evidence_file not in compile_files:
            errors.append(f"{label} references evidence file outside compile unit: {evidence_file}")
            continue

        if evidence_file not in line_cache:
            evidence_path = ROOT / evidence_file
            if not evidence_path.exists():
                errors.append(f"{label} references missing evidence file: {evidence_file}")
                continue
            line_cache[evidence_file] = evidence_path.read_text(encoding="utf-8").splitlines()

        file_lines = line_cache[evidence_file]
        if line_end > len(file_lines):
            errors.append(
                f"{label} references line {line_end} past end of file {evidence_file} "
                f"with {len(file_lines)} lines"
            )


def validate_clock_reset_record(record: dict, *, record_path: Path, errors: list[str]) -> None:
    record_label = rel(record_path)
    require_keys(
        record,
        ["record_id", "schema_version", "task", "input", "target", "metadata", "provenance"],
        label=record_label,
        errors=errors,
    )
    if errors and any(message.startswith(f"{record_label} is missing keys") for message in errors):
        return

    record_id = record["record_id"]
    schema_version = record["schema_version"]
    if not isinstance(record_id, str) or not record_id:
        errors.append(f"{record_label} has invalid record_id")
    if not isinstance(schema_version, str) or not SEMVER_RE.match(schema_version):
        errors.append(f"{record_label} has invalid schema_version: {schema_version}")
    if record.get("task") != "clock_reset_extraction":
        errors.append(f"{record_label} has unsupported task: {record.get('task')}")

    input_data = record.get("input")
    target = record.get("target")
    metadata = record.get("metadata")
    provenance = record.get("provenance")
    if not all(isinstance(item, dict) for item in (input_data, target, metadata, provenance)):
        errors.append(f"{record_label} must use object-valued input/target/metadata/provenance")
        return

    require_keys(
        input_data,
        ["language", "top_module", "rtl_text", "compile_unit"],
        label=f"{record_label} input",
        errors=errors,
    )
    require_keys(
        target,
        ["clocks", "resets", "summary"],
        label=f"{record_label} target",
        errors=errors,
    )
    require_keys(
        metadata,
        ["source_type", "source_group", "difficulty"],
        label=f"{record_label} metadata",
        errors=errors,
    )
    require_keys(
        provenance,
        [
            "license",
            "origin_repo",
            "origin_path",
            "generator",
            "generator_version",
            "human_review_status",
        ],
        label=f"{record_label} provenance",
        errors=errors,
    )

    compile_unit = input_data.get("compile_unit")
    if not isinstance(compile_unit, dict):
        errors.append(f"{record_label} input.compile_unit must be an object")
        return
    require_keys(compile_unit, ["files", "filelist"], label=f"{record_label} compile_unit", errors=errors)

    compile_files = compile_unit.get("files")
    filelist = compile_unit.get("filelist")
    if not isinstance(compile_files, list) or not compile_files or not all(isinstance(path, str) for path in compile_files):
        errors.append(f"{record_label} compile_unit.files must be a non-empty string list")
        return
    if filelist is not None and not isinstance(filelist, str):
        errors.append(f"{record_label} compile_unit.filelist must be a string or null")

    compile_file_set = set(compile_files)
    for source_file in compile_files:
        source_path = ROOT / source_file
        if not source_path.exists():
            errors.append(f"{record_label} references missing compile-unit file: {source_file}")
    if isinstance(filelist, str) and not (ROOT / filelist).exists():
        errors.append(f"{record_label} references missing filelist: {filelist}")

    rtl_text = input_data.get("rtl_text")
    if not isinstance(rtl_text, str) or not rtl_text:
        errors.append(f"{record_label} input.rtl_text must be a non-empty string")
    elif len(compile_files) == 1 and filelist is None:
        source_text = (ROOT / compile_files[0]).read_text(encoding="utf-8")
        if rtl_text != source_text:
            errors.append(f"{record_label} rtl_text does not match {compile_files[0]}")

    line_cache: dict[str, list[str]] = {}
    clocks = target.get("clocks")
    resets = target.get("resets")
    summary = target.get("summary")
    if not isinstance(clocks, list) or not clocks:
        errors.append(f"{record_label} target.clocks must be a non-empty list")
    if not isinstance(resets, list):
        errors.append(f"{record_label} target.resets must be a list")
    if not isinstance(summary, dict):
        errors.append(f"{record_label} target.summary must be an object")
        summary = {}

    clock_names: set[str] = set()
    reset_names: set[str] = set()

    if isinstance(clocks, list):
        for index, clock in enumerate(clocks):
            label = f"{record_label} clock[{index}]"
            if not isinstance(clock, dict):
                errors.append(f"{label} must be an object")
                continue
            require_keys(clock, ["name", "edge", "evidence"], label=label, errors=errors)
            name = clock.get("name")
            if not isinstance(name, str) or not name:
                errors.append(f"{label} must have a non-empty name")
            elif name in clock_names:
                errors.append(f"{record_label} uses duplicate clock name: {name}")
            else:
                clock_names.add(name)
            validate_evidence_spans(
                clock.get("evidence"),
                label=label,
                compile_files=compile_file_set,
                line_cache=line_cache,
                errors=errors,
            )

    if isinstance(resets, list):
        for index, reset in enumerate(resets):
            label = f"{record_label} reset[{index}]"
            if not isinstance(reset, dict):
                errors.append(f"{label} must be an object")
                continue
            require_keys(reset, ["name", "edge", "active_level", "style", "evidence"], label=label, errors=errors)
            name = reset.get("name")
            if not isinstance(name, str) or not name:
                errors.append(f"{label} must have a non-empty name")
            elif name in reset_names:
                errors.append(f"{record_label} uses duplicate reset name: {name}")
            else:
                reset_names.add(name)
            validate_evidence_spans(
                reset.get("evidence"),
                label=label,
                compile_files=compile_file_set,
                line_cache=line_cache,
                errors=errors,
            )

    if isinstance(summary, dict):
        for key in ("clock_count", "reset_count", "domain_count"):
            value = summary.get(key)
            if not isinstance(value, int) or value < 0:
                errors.append(f"{record_label} summary.{key} must be a non-negative integer")

        if isinstance(clocks, list) and summary.get("clock_count") != len(clocks):
            errors.append(f"{record_label} summary.clock_count does not match target.clocks length")
        if isinstance(resets, list) and summary.get("reset_count") != len(resets):
            errors.append(f"{record_label} summary.reset_count does not match target.resets length")
        if summary.get("domain_count") != len(clock_names):
            errors.append(f"{record_label} summary.domain_count does not match unique clock count")

    provenance_yaml_path = record_path.with_name("provenance.yaml")
    if not provenance_yaml_path.exists():
        errors.append(f"{record_label} is missing provenance.yaml")
        return

    provenance_yaml = load_yaml(provenance_yaml_path)
    for key in (
        "source_type",
        "source_group",
        "top_module",
        "origin_repo",
        "origin_commit",
        "origin_path",
        "license",
        "generator",
        "generator_version",
        "mutation_id",
        "human_review_status",
    ):
        if key not in provenance_yaml:
            errors.append(f"{rel(provenance_yaml_path)} is missing key: {key}")

    if provenance.get("license") != provenance_yaml.get("license"):
        errors.append(f"{record_label} license does not match {rel(provenance_yaml_path)}")
    if provenance.get("origin_path") != provenance_yaml.get("origin_path"):
        errors.append(f"{record_label} origin_path does not match {rel(provenance_yaml_path)}")
    if provenance.get("generator") != provenance_yaml.get("generator"):
        errors.append(f"{record_label} generator does not match {rel(provenance_yaml_path)}")
    if provenance.get("generator_version") != provenance_yaml.get("generator_version"):
        errors.append(f"{record_label} generator_version does not match {rel(provenance_yaml_path)}")
    if provenance.get("mutation_id") != provenance_yaml.get("mutation_id"):
        errors.append(f"{record_label} mutation_id does not match {rel(provenance_yaml_path)}")
    if provenance.get("human_review_status") != provenance_yaml.get("human_review_status"):
        errors.append(f"{record_label} human_review_status does not match {rel(provenance_yaml_path)}")
    if metadata.get("source_type") != provenance_yaml.get("source_type"):
        errors.append(f"{record_label} metadata.source_type does not match {rel(provenance_yaml_path)}")
    if metadata.get("source_group") != provenance_yaml.get("source_group"):
        errors.append(f"{record_label} metadata.source_group does not match {rel(provenance_yaml_path)}")
    if input_data.get("top_module") != provenance_yaml.get("top_module"):
        errors.append(f"{record_label} input.top_module does not match {rel(provenance_yaml_path)}")

    origin_path = provenance.get("origin_path")
    if isinstance(origin_path, str) and not (ROOT / origin_path).exists():
        errors.append(f"{record_label} provenance.origin_path does not exist: {origin_path}")


def validate_splits(corpus_dir: Path, record_ids: set[str], errors: list[str]) -> None:
    splits_dir = corpus_dir / "splits"
    if not splits_dir.exists():
        errors.append(f"{rel(corpus_dir)} is missing splits/")
        return

    assigned_ids: dict[str, str] = {}
    for split_name in SPLIT_NAMES:
        split_path = splits_dir / f"{split_name}.txt"
        if not split_path.exists():
            errors.append(f"{rel(corpus_dir)} is missing split file: {rel(split_path)}")
            continue

        seen_in_split: set[str] = set()
        for line in split_path.read_text(encoding="utf-8").splitlines():
            entry = line.strip()
            if not entry or entry.startswith("#"):
                continue
            if entry in seen_in_split:
                errors.append(f"{rel(split_path)} contains duplicate record id: {entry}")
                continue
            seen_in_split.add(entry)
            if entry not in record_ids:
                errors.append(f"{rel(split_path)} references unknown record id: {entry}")
                continue
            previous_split = assigned_ids.get(entry)
            if previous_split is not None:
                errors.append(
                    f"record id {entry} appears in both {previous_split} and {rel(split_path)}"
                )
                continue
            assigned_ids[entry] = rel(split_path)

    if record_ids != set(assigned_ids):
        missing = sorted(record_ids - set(assigned_ids))
        for record_id in missing:
            errors.append(f"{rel(corpus_dir)} does not assign record id to a split: {record_id}")


def validate_corpus(corpus_dir: Path, errors: list[str]) -> int:
    record_paths = sorted(corpus_dir.glob("cases/*/record.json"))
    if not record_paths:
        errors.append(f"{rel(corpus_dir)} does not contain any record.json files")
        return 0

    record_ids: set[str] = set()
    for record_path in record_paths:
        try:
            record = load_json(record_path)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON in {rel(record_path)}: {exc}")
            continue

        if not isinstance(record, dict):
            errors.append(f"{rel(record_path)} must contain one JSON object")
            continue

        record_id = record.get("record_id")
        if isinstance(record_id, str):
            if record_id in record_ids:
                errors.append(f"{rel(corpus_dir)} contains duplicate record_id: {record_id}")
            else:
                record_ids.add(record_id)

        validate_clock_reset_record(record, record_path=record_path, errors=errors)

    validate_splits(corpus_dir, record_ids, errors)
    return len(record_paths)


def main() -> int:
    errors: list[str] = []

    for required_path in (
        SCHEMAS_DIR / "rtl-record-common.schema.json",
        SCHEMAS_DIR / "rtl-understanding.schema.json",
    ):
        if not required_path.exists():
            errors.append(f"missing dataset schema file: {rel(required_path)}")

    if not CORPORA_DIR.exists():
        errors.append("datasets/corpora/ does not exist")
    corpus_dirs = sorted(path for path in CORPORA_DIR.iterdir() if path.is_dir()) if CORPORA_DIR.exists() else []
    if not corpus_dirs:
        errors.append("no dataset corpora found under datasets/corpora/")

    record_count = 0
    for corpus_dir in corpus_dirs:
        record_count += validate_corpus(corpus_dir, errors)

    if errors:
        print("dataset corpus validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"dataset corpus validation passed for {record_count} records across {len(corpus_dirs)} corpora")
    return 0


if __name__ == "__main__":
    sys.exit(main())
