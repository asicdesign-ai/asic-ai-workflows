#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from pathlib import Path


CDC_ID_RE = re.compile(r"^CDC-\d{3}$")
PATH_ID_RE = re.compile(r"^PATH-\d{3}$")
OBJ_ID_RE = re.compile(r"^OBJ-\d{3}$")
REQ_ID_RE = re.compile(r"^REQ-\d{3}$")
BEH_ID_RE = re.compile(r"^BEH-\d{3}$")
TEST_ID_RE = re.compile(r"^TEST-\d{3}$")
SVA_ID_RE = re.compile(r"^SVA-\d{3}$")
COV_ID_RE = re.compile(r"^COV-\d{3}$")
RISK_ID_RE = re.compile(r"^RISK-\d{3}$")
LINT_ID_RE = re.compile(r"^LINT-\d{3}$")
RDC_ID_RE = re.compile(r"^RDC-\d{3}$")
UNR_ID_RE = re.compile(r"^UNR-\d{3}$")
VIEW_ID_RE = re.compile(r"^VIEW-\d{3}$")
SEQ_ID_RE = re.compile(r"^SEQ-\d{3}$")
COMB_ID_RE = re.compile(r"^COMB-\d{3}$")


class ValidationError(Exception):
    pass


def load_json_like_yaml(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON-compatible YAML: {exc}") from exc


def require_keys(obj: dict, keys: list[str], context: str) -> None:
    for key in keys:
        if key not in obj:
            raise ValidationError(f"{context} is missing required key: {key}")


def require_type(value, expected_type, context: str) -> None:
    if not isinstance(value, expected_type):
        raise ValidationError(f"{context} has wrong type: expected {expected_type.__name__}")


def require_optional_type(value, expected_type, context: str) -> None:
    if value is None:
        return
    require_type(value, expected_type, context)


def require_enum(value, valid_values: set[str], context: str) -> None:
    if value not in valid_values:
        raise ValidationError(f"{context} is invalid")


def require_string_list(value, context: str, allow_empty: bool = True) -> None:
    require_type(value, list, context)
    if not allow_empty and not value:
        raise ValidationError(f"{context} must be a non-empty list")
    if not all(isinstance(item, str) for item in value):
        raise ValidationError(f"{context} must contain only strings")


def validate_line_field(value, context: str) -> None:
    if isinstance(value, int):
        return
    if isinstance(value, list) and value and all(isinstance(item, int) for item in value):
        return
    raise ValidationError(f"{context} must be an integer or a non-empty list of integers")


def validate_design_context(
    design: dict,
    context: str,
    *,
    require_rtl_files: bool = False,
    require_intent_summary: bool = False,
) -> None:
    require_type(design, dict, context)
    require_keys(design, ["top_module"], context)
    require_type(design["top_module"], str, f"{context}.top_module")
    if require_rtl_files:
        require_keys(design, ["rtl_files"], context)
        require_string_list(design["rtl_files"], f"{context}.rtl_files", allow_empty=False)
    if require_intent_summary:
        require_keys(design, ["intent_summary"], context)
        require_type(design["intent_summary"], str, f"{context}.intent_summary")


def validate_hdl_design_view(data: dict) -> None:
    require_type(data, dict, "hdl design view")
    require_keys(
        data,
        [
            "design",
            "extraction",
            "ports",
            "signals",
            "sequential_elements",
            "combinational_nodes",
            "instances",
            "unresolved",
            "summary",
        ],
        "hdl design view",
    )

    valid_languages = {"systemverilog", "verilog", "vhdl", "proprietary", "unknown"}
    valid_view_formats = {"uhdm_text", "ast_json", "tool_design_graph", "model_derived"}
    valid_source_kinds = {"rtl_source", "uhdm_dump", "ast_json", "tool_output", "manual"}
    valid_confidence = {"high", "medium", "low"}

    design = data["design"]
    require_type(design, dict, "hdl design view.design")
    require_keys(design, ["view_id", "top_units", "source_language", "source_files"], "hdl design view.design")
    if not VIEW_ID_RE.match(design["view_id"]):
        raise ValidationError("hdl design view.design.view_id must match VIEW-NNN")
    require_string_list(design["top_units"], "hdl design view.design.top_units", allow_empty=False)
    require_enum(design["source_language"], valid_languages, "hdl design view.design.source_language")
    require_string_list(design["source_files"], "hdl design view.design.source_files", allow_empty=False)

    extraction = data["extraction"]
    require_type(extraction, dict, "hdl design view.extraction")
    require_keys(extraction, ["view_format", "source_kind", "tool", "confidence"], "hdl design view.extraction")
    require_enum(extraction["view_format"], valid_view_formats, "hdl design view.extraction.view_format")
    require_enum(extraction["source_kind"], valid_source_kinds, "hdl design view.extraction.source_kind")
    require_enum(extraction["confidence"], valid_confidence, "hdl design view.extraction.confidence")
    require_type(extraction["tool"], dict, "hdl design view.extraction.tool")
    require_keys(extraction["tool"], ["name", "version", "evidence"], "hdl design view.extraction.tool")
    require_type(extraction["tool"]["name"], str, "hdl design view.extraction.tool.name")
    require_optional_type(extraction["tool"]["version"], str, "hdl design view.extraction.tool.version")
    require_type(extraction["tool"]["evidence"], str, "hdl design view.extraction.tool.evidence")

    valid_directions = {"input", "output", "inout"}
    valid_roles = {"clock", "reset", "control", "data", "status", "interrupt", "handshake", "unknown"}
    require_type(data["ports"], list, "hdl design view.ports")
    for index, item in enumerate(data["ports"], start=1):
        context = f"hdl design view.ports[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["name", "direction", "width", "role", "line"], context)
        require_type(item["name"], str, f"{context}.name")
        require_enum(item["direction"], valid_directions, f"{context}.direction")
        require_type(item["width"], int, f"{context}.width")
        require_enum(item["role"], valid_roles, f"{context}.role")
        require_type(item["line"], int, f"{context}.line")

    valid_signal_kinds = {"register", "wire", "memory", "port", "unknown"}
    require_type(data["signals"], list, "hdl design view.signals")
    for index, item in enumerate(data["signals"], start=1):
        context = f"hdl design view.signals[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["name", "width", "kind", "line"], context)
        require_type(item["name"], str, f"{context}.name")
        require_type(item["width"], int, f"{context}.width")
        require_enum(item["kind"], valid_signal_kinds, f"{context}.kind")
        require_type(item["line"], int, f"{context}.line")

    valid_seq_kinds = {"flip_flop", "latch", "memory", "unknown"}
    require_type(data["sequential_elements"], list, "hdl design view.sequential_elements")
    for index, item in enumerate(data["sequential_elements"], start=1):
        context = f"hdl design view.sequential_elements[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["id", "name", "kind", "width", "clock", "reset", "evidence", "line", "confidence"], context)
        if not SEQ_ID_RE.match(item["id"]):
            raise ValidationError(f"{context}.id must match SEQ-NNN")
        require_type(item["name"], str, f"{context}.name")
        require_enum(item["kind"], valid_seq_kinds, f"{context}.kind")
        require_type(item["width"], int, f"{context}.width")
        require_type(item["clock"], str, f"{context}.clock")
        require_optional_type(item["reset"], str, f"{context}.reset")
        require_type(item["evidence"], str, f"{context}.evidence")
        require_type(item["line"], int, f"{context}.line")
        require_enum(item["confidence"], valid_confidence, f"{context}.confidence")

    require_type(data["combinational_nodes"], list, "hdl design view.combinational_nodes")
    for index, item in enumerate(data["combinational_nodes"], start=1):
        context = f"hdl design view.combinational_nodes[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["id", "op", "output", "inputs", "width", "line", "confidence"], context)
        if not COMB_ID_RE.match(item["id"]):
            raise ValidationError(f"{context}.id must match COMB-NNN")
        require_type(item["op"], str, f"{context}.op")
        require_type(item["output"], str, f"{context}.output")
        require_string_list(item["inputs"], f"{context}.inputs", allow_empty=False)
        require_type(item["width"], int, f"{context}.width")
        require_type(item["line"], int, f"{context}.line")
        require_enum(item["confidence"], valid_confidence, f"{context}.confidence")

    require_type(data["instances"], list, "hdl design view.instances")
    require_type(data["unresolved"], list, "hdl design view.unresolved")
    for index, item in enumerate(data["unresolved"], start=1):
        context = f"hdl design view.unresolved[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["name", "line", "reason"], context)
        require_type(item["name"], str, f"{context}.name")
        require_type(item["line"], int, f"{context}.line")
        require_type(item["reason"], str, f"{context}.reason")

    summary = data["summary"]
    require_type(summary, dict, "hdl design view.summary")
    require_keys(
        summary,
        [
            "total_design_units",
            "total_ports",
            "total_sequential_elements",
            "total_combinational_nodes",
            "total_instances",
            "total_unresolved",
        ],
        "hdl design view.summary",
    )
    for key, value in summary.items():
        require_type(value, int, f"hdl design view.summary.{key}")


def validate_objective_ids(value, context: str) -> None:
    require_string_list(value, context, allow_empty=False)
    for item in value:
        if not OBJ_ID_RE.match(item):
            raise ValidationError(f"{context} contains an invalid objective id: {item}")


def validate_objectives_list(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_priorities = {"must", "should", "could"}
    valid_sources = {"design_intent", "rtl", "both"}
    valid_categories = {
        "reset",
        "configuration",
        "data_path",
        "control",
        "status",
        "interrupt",
        "error_handling",
        "performance",
    }

    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(
            item,
            ["id", "title", "priority", "source", "category", "description", "success_condition"],
            item_context,
        )
        if not OBJ_ID_RE.match(item["id"]):
            raise ValidationError(f"{item_context}.id must match OBJ-NNN")
        require_type(item["title"], str, f"{item_context}.title")
        require_enum(item["priority"], valid_priorities, f"{item_context}.priority")
        require_enum(item["source"], valid_sources, f"{item_context}.source")
        require_enum(item["category"], valid_categories, f"{item_context}.category")
        require_type(item["description"], str, f"{item_context}.description")
        require_type(item["success_condition"], str, f"{item_context}.success_condition")


def validate_summary_priority(summary: dict, context: str) -> None:
    require_keys(summary, ["total_objectives", "by_priority"], context)
    require_type(summary["total_objectives"], int, f"{context}.total_objectives")
    require_type(summary["by_priority"], dict, f"{context}.by_priority")
    require_keys(summary["by_priority"], ["must", "should", "could"], f"{context}.by_priority")
    for key, value in summary["by_priority"].items():
        require_type(value, int, f"{context}.by_priority.{key}")


def validate_dv_objectives(data: dict) -> None:
    require_type(data, dict, "dv objectives report")
    require_keys(data, ["design", "objectives", "summary"], "dv objectives report")
    validate_design_context(
        data["design"],
        "dv objectives report.design",
        require_rtl_files=True,
        require_intent_summary=True,
    )
    validate_objectives_list(data["objectives"], "dv objectives report.objectives")
    require_type(data["summary"], dict, "dv objectives report.summary")
    validate_summary_priority(data["summary"], "dv objectives report.summary")


def validate_rtl_verification_surface(data: dict) -> None:
    require_type(data, dict, "rtl verification surface report")
    require_keys(
        data,
        [
            "design",
            "clocks",
            "resets",
            "interfaces",
            "state_elements",
            "behaviors",
            "observability",
            "unresolved",
            "summary",
        ],
        "rtl verification surface report",
    )
    validate_design_context(
        data["design"],
        "rtl verification surface report.design",
        require_rtl_files=True,
    )

    require_type(data["clocks"], list, "rtl verification surface report.clocks")
    for index, item in enumerate(data["clocks"], start=1):
        context = f"rtl verification surface report.clocks[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["name", "line"], context)
        require_type(item["name"], str, f"{context}.name")
        require_type(item["line"], int, f"{context}.line")

    valid_reset_active = {"active_high", "active_low"}
    valid_reset_style = {"sync", "async"}
    require_type(data["resets"], list, "rtl verification surface report.resets")
    for index, item in enumerate(data["resets"], start=1):
        context = f"rtl verification surface report.resets[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["name", "active", "style", "line"], context)
        require_type(item["name"], str, f"{context}.name")
        require_enum(item["active"], valid_reset_active, f"{context}.active")
        require_enum(item["style"], valid_reset_style, f"{context}.style")
        require_type(item["line"], int, f"{context}.line")

    valid_direction = {"input", "output", "inout"}
    valid_interface_role = {
        "clock",
        "reset",
        "config",
        "data",
        "status",
        "interrupt",
        "handshake",
        "command",
        "response",
    }
    require_type(data["interfaces"], list, "rtl verification surface report.interfaces")
    for index, item in enumerate(data["interfaces"], start=1):
        context = f"rtl verification surface report.interfaces[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["name", "direction", "role", "width", "line"], context)
        require_type(item["name"], str, f"{context}.name")
        require_enum(item["direction"], valid_direction, f"{context}.direction")
        require_enum(item["role"], valid_interface_role, f"{context}.role")
        require_type(item["width"], int, f"{context}.width")
        require_type(item["line"], int, f"{context}.line")

    valid_state_kind = {"fsm_state", "counter", "register", "flag", "pointer", "buffer"}
    require_type(data["state_elements"], list, "rtl verification surface report.state_elements")
    for index, item in enumerate(data["state_elements"], start=1):
        context = f"rtl verification surface report.state_elements[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["name", "kind", "clock", "line"], context)
        require_type(item["name"], str, f"{context}.name")
        require_enum(item["kind"], valid_state_kind, f"{context}.kind")
        require_type(item["clock"], str, f"{context}.clock")
        require_type(item["line"], int, f"{context}.line")

    valid_behavior_kind = {
        "reset",
        "configuration",
        "transaction",
        "status",
        "error",
        "backpressure",
        "interrupt",
        "state_transition",
    }
    require_type(data["behaviors"], list, "rtl verification surface report.behaviors")
    for index, item in enumerate(data["behaviors"], start=1):
        context = f"rtl verification surface report.behaviors[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["id", "kind", "description", "evidence"], context)
        if not BEH_ID_RE.match(item["id"]):
            raise ValidationError(f"{context}.id must match BEH-NNN")
        require_enum(item["kind"], valid_behavior_kind, f"{context}.kind")
        require_type(item["description"], str, f"{context}.description")
        require_type(item["evidence"], list, f"{context}.evidence")
        if not item["evidence"]:
            raise ValidationError(f"{context}.evidence must be a non-empty list")
        for ev_index, evidence in enumerate(item["evidence"], start=1):
            ev_context = f"{context}.evidence[{ev_index}]"
            require_type(evidence, dict, ev_context)
            require_keys(evidence, ["file", "line", "signal"], ev_context)
            require_type(evidence["file"], str, f"{ev_context}.file")
            require_type(evidence["line"], int, f"{ev_context}.line")
            require_type(evidence["signal"], str, f"{ev_context}.signal")

    valid_observability_role = {"status", "interrupt", "error", "counter", "state"}
    require_type(data["observability"], list, "rtl verification surface report.observability")
    for index, item in enumerate(data["observability"], start=1):
        context = f"rtl verification surface report.observability[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["signal", "role", "line"], context)
        require_type(item["signal"], str, f"{context}.signal")
        require_enum(item["role"], valid_observability_role, f"{context}.role")
        require_type(item["line"], int, f"{context}.line")

    require_type(data["unresolved"], list, "rtl verification surface report.unresolved")
    for index, item in enumerate(data["unresolved"], start=1):
        context = f"rtl verification surface report.unresolved[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["name", "reason", "line"], context)
        require_type(item["name"], str, f"{context}.name")
        require_type(item["reason"], str, f"{context}.reason")
        require_type(item["line"], int, f"{context}.line")

    summary = data["summary"]
    require_type(summary, dict, "rtl verification surface report.summary")
    require_keys(
        summary,
        ["total_interfaces", "total_state_elements", "total_behaviors", "total_unresolved"],
        "rtl verification surface report.summary",
    )
    require_type(summary["total_interfaces"], int, "rtl verification surface report.summary.total_interfaces")
    require_type(
        summary["total_state_elements"],
        int,
        "rtl verification surface report.summary.total_state_elements",
    )
    require_type(summary["total_behaviors"], int, "rtl verification surface report.summary.total_behaviors")
    require_type(summary["total_unresolved"], int, "rtl verification surface report.summary.total_unresolved")


def validate_uvm_env(env: dict, context: str) -> None:
    require_type(env, dict, context)
    require_keys(
        env,
        ["bench_style", "agents", "monitors", "scoreboards", "reference_models", "virtual_sequences"],
        context,
    )
    require_type(env["bench_style"], str, f"{context}.bench_style")

    valid_agent_mode = {"active", "passive"}
    for section in ("agents", "monitors", "scoreboards", "reference_models", "virtual_sequences"):
        require_type(env[section], list, f"{context}.{section}")

    for index, item in enumerate(env["agents"], start=1):
        item_context = f"{context}.agents[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["name", "interface", "mode", "justification"], item_context)
        require_type(item["name"], str, f"{item_context}.name")
        require_type(item["interface"], str, f"{item_context}.interface")
        require_enum(item["mode"], valid_agent_mode, f"{item_context}.mode")
        require_type(item["justification"], str, f"{item_context}.justification")

    for index, item in enumerate(env["monitors"], start=1):
        item_context = f"{context}.monitors[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["name", "interface", "justification"], item_context)
        require_type(item["name"], str, f"{item_context}.name")
        require_type(item["interface"], str, f"{item_context}.interface")
        require_type(item["justification"], str, f"{item_context}.justification")

    for index, item in enumerate(env["scoreboards"], start=1):
        item_context = f"{context}.scoreboards[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["name", "compares", "justification"], item_context)
        require_type(item["name"], str, f"{item_context}.name")
        require_type(item["compares"], str, f"{item_context}.compares")
        require_type(item["justification"], str, f"{item_context}.justification")

    for index, item in enumerate(env["reference_models"], start=1):
        item_context = f"{context}.reference_models[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["name", "scope"], item_context)
        require_type(item["name"], str, f"{item_context}.name")
        require_type(item["scope"], str, f"{item_context}.scope")

    for index, item in enumerate(env["virtual_sequences"], start=1):
        item_context = f"{context}.virtual_sequences[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["name", "objective_ids", "description"], item_context)
        require_type(item["name"], str, f"{item_context}.name")
        validate_objective_ids(item["objective_ids"], f"{item_context}.objective_ids")
        require_type(item["description"], str, f"{item_context}.description")


def validate_tests_list(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_priority = {"must", "should", "could"}
    valid_stimulus = {"directed", "constrained_random", "virtual_sequence"}
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(
            item,
            ["id", "title", "objective_ids", "stimulus", "checkers", "priority", "description"],
            item_context,
        )
        if not TEST_ID_RE.match(item["id"]):
            raise ValidationError(f"{item_context}.id must match TEST-NNN")
        require_type(item["title"], str, f"{item_context}.title")
        validate_objective_ids(item["objective_ids"], f"{item_context}.objective_ids")
        require_enum(item["stimulus"], valid_stimulus, f"{item_context}.stimulus")
        require_string_list(item["checkers"], f"{item_context}.checkers")
        require_enum(item["priority"], valid_priority, f"{item_context}.priority")
        require_type(item["description"], str, f"{item_context}.description")


def validate_test_summary(summary: dict, context: str) -> None:
    require_type(summary, dict, context)
    require_keys(summary, ["total_tests", "by_priority"], context)
    require_type(summary["total_tests"], int, f"{context}.total_tests")
    require_type(summary["by_priority"], dict, f"{context}.by_priority")
    require_keys(summary["by_priority"], ["must", "should", "could"], f"{context}.by_priority")
    for key, value in summary["by_priority"].items():
        require_type(value, int, f"{context}.by_priority.{key}")


def validate_uvm_test_plan(data: dict) -> None:
    require_type(data, dict, "uvm test plan report")
    require_keys(data, ["design", "env", "tests", "summary"], "uvm test plan report")
    validate_design_context(data["design"], "uvm test plan report.design")
    validate_uvm_env(data["env"], "uvm test plan report.env")
    validate_tests_list(data["tests"], "uvm test plan report.tests")
    validate_test_summary(data["summary"], "uvm test plan report.summary")


def validate_assertions_list(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_classes = {"reset", "protocol", "state", "data_integrity", "error"}
    valid_sources = {"design_intent", "rtl", "both"}
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["id", "title", "objective_ids", "class", "source", "bind_target", "description"], item_context)
        if not SVA_ID_RE.match(item["id"]):
            raise ValidationError(f"{item_context}.id must match SVA-NNN")
        require_type(item["title"], str, f"{item_context}.title")
        validate_objective_ids(item["objective_ids"], f"{item_context}.objective_ids")
        require_enum(item["class"], valid_classes, f"{item_context}.class")
        require_enum(item["source"], valid_sources, f"{item_context}.source")
        require_type(item["bind_target"], str, f"{item_context}.bind_target")
        require_type(item["description"], str, f"{item_context}.description")


def validate_sva_plan(data: dict) -> None:
    require_type(data, dict, "sva plan report")
    require_keys(data, ["design", "assertions", "summary"], "sva plan report")
    validate_design_context(data["design"], "sva plan report.design")
    validate_assertions_list(data["assertions"], "sva plan report.assertions")
    summary = data["summary"]
    require_type(summary, dict, "sva plan report.summary")
    require_keys(summary, ["total_assertions", "by_class"], "sva plan report.summary")
    require_type(summary["total_assertions"], int, "sva plan report.summary.total_assertions")
    require_type(summary["by_class"], dict, "sva plan report.summary.by_class")
    require_keys(
        summary["by_class"],
        ["reset", "protocol", "state", "data_integrity", "error"],
        "sva plan report.summary.by_class",
    )
    for key, value in summary["by_class"].items():
        require_type(value, int, f"sva plan report.summary.by_class.{key}")


def validate_coverage_entry(
    item: dict,
    context: str,
    *,
    require_target: bool = False,
    require_targets: bool = False,
    require_related_targets: bool = False,
) -> None:
    require_type(item, dict, context)
    require_keys(item, ["id", "objective_ids"], context)
    if not COV_ID_RE.match(item["id"]):
        raise ValidationError(f"{context}.id must match COV-NNN")
    validate_objective_ids(item["objective_ids"], f"{context}.objective_ids")
    if require_target:
        require_keys(item, ["target", "kind", "description"], context)
        require_type(item["target"], str, f"{context}.target")
        require_type(item["description"], str, f"{context}.description")
    if require_targets:
        require_keys(item, ["targets", "description"], context)
        require_string_list(item["targets"], f"{context}.targets", allow_empty=False)
        require_type(item["description"], str, f"{context}.description")
    if require_related_targets:
        require_keys(item, ["related_targets", "rationale"], context)
        require_string_list(item["related_targets"], f"{context}.related_targets", allow_empty=False)
        require_type(item["rationale"], str, f"{context}.rationale")


def validate_coverage_sections(coverage: dict, context: str) -> None:
    require_type(coverage, dict, context)
    require_keys(coverage, ["coverpoints", "crosses", "exclusions"], context)

    valid_coverpoint_kind = {"state", "configuration", "data", "status", "error", "interrupt"}

    require_type(coverage["coverpoints"], list, f"{context}.coverpoints")
    for index, item in enumerate(coverage["coverpoints"], start=1):
        item_context = f"{context}.coverpoints[{index}]"
        validate_coverage_entry(item, item_context, require_target=True)
        require_enum(item["kind"], valid_coverpoint_kind, f"{item_context}.kind")

    require_type(coverage["crosses"], list, f"{context}.crosses")
    for index, item in enumerate(coverage["crosses"], start=1):
        item_context = f"{context}.crosses[{index}]"
        validate_coverage_entry(item, item_context, require_targets=True)

    require_type(coverage["exclusions"], list, f"{context}.exclusions")
    for index, item in enumerate(coverage["exclusions"], start=1):
        item_context = f"{context}.exclusions[{index}]"
        validate_coverage_entry(item, item_context, require_related_targets=True)


def validate_dv_coverage_plan(data: dict) -> None:
    require_type(data, dict, "dv coverage plan report")
    require_keys(data, ["design", "coverpoints", "crosses", "exclusions", "summary"], "dv coverage plan report")
    validate_design_context(data["design"], "dv coverage plan report.design")
    validate_coverage_sections(
        {
            "coverpoints": data["coverpoints"],
            "crosses": data["crosses"],
            "exclusions": data["exclusions"],
        },
        "dv coverage plan report",
    )
    summary = data["summary"]
    require_type(summary, dict, "dv coverage plan report.summary")
    require_keys(
        summary,
        ["total_coverpoints", "total_crosses", "total_exclusions"],
        "dv coverage plan report.summary",
    )
    require_type(summary["total_coverpoints"], int, "dv coverage plan report.summary.total_coverpoints")
    require_type(summary["total_crosses"], int, "dv coverage plan report.summary.total_crosses")
    require_type(summary["total_exclusions"], int, "dv coverage plan report.summary.total_exclusions")


def validate_interfaces_for_plan(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_direction = {"input", "output", "inout"}
    valid_interface_role = {
        "clock",
        "reset",
        "config",
        "data",
        "status",
        "interrupt",
        "handshake",
        "command",
        "response",
    }
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["name", "direction", "role", "width"], item_context)
        require_type(item["name"], str, f"{item_context}.name")
        require_enum(item["direction"], valid_direction, f"{item_context}.direction")
        require_enum(item["role"], valid_interface_role, f"{item_context}.role")
        require_type(item["width"], int, f"{item_context}.width")


def validate_risks(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_sources = {"cdc_report", "timing_report", "rtl", "intent_conflict"}
    valid_severity = {"critical", "high", "medium", "low"}
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["id", "source", "severity", "objective_ids", "description"], item_context)
        if not RISK_ID_RE.match(item["id"]):
            raise ValidationError(f"{item_context}.id must match RISK-NNN")
        require_enum(item["source"], valid_sources, f"{item_context}.source")
        require_enum(item["severity"], valid_severity, f"{item_context}.severity")
        validate_objective_ids(item["objective_ids"], f"{item_context}.objective_ids")
        require_type(item["description"], str, f"{item_context}.description")


def validate_unresolved(value: list, context: str) -> None:
    require_type(value, list, context)
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["id", "item", "reason", "objective_ids"], item_context)
        if not UNR_ID_RE.match(item["id"]):
            raise ValidationError(f"{item_context}.id must match UNR-NNN")
        require_type(item["item"], str, f"{item_context}.item")
        require_type(item["reason"], str, f"{item_context}.reason")
        validate_objective_ids(item["objective_ids"], f"{item_context}.objective_ids")


def validate_dv_plan(data: dict) -> None:
    require_type(data, dict, "dv plan report")
    require_keys(
        data,
        ["design", "objectives", "interfaces", "env", "tests", "assertions", "coverage", "risks", "unresolved", "summary"],
        "dv plan report",
    )
    validate_design_context(
        data["design"],
        "dv plan report.design",
        require_rtl_files=True,
        require_intent_summary=True,
    )
    validate_objectives_list(data["objectives"], "dv plan report.objectives")
    validate_interfaces_for_plan(data["interfaces"], "dv plan report.interfaces")
    validate_uvm_env(data["env"], "dv plan report.env")
    validate_tests_list(data["tests"], "dv plan report.tests")
    validate_assertions_list(data["assertions"], "dv plan report.assertions")
    validate_coverage_sections(data["coverage"], "dv plan report.coverage")
    validate_risks(data["risks"], "dv plan report.risks")
    validate_unresolved(data["unresolved"], "dv plan report.unresolved")

    summary = data["summary"]
    require_type(summary, dict, "dv plan report.summary")
    require_keys(
        summary,
        [
            "total_objectives",
            "total_tests",
            "total_assertions",
            "total_coverage_items",
            "total_risks",
            "total_unresolved",
        ],
        "dv plan report.summary",
    )
    require_type(summary["total_objectives"], int, "dv plan report.summary.total_objectives")
    require_type(summary["total_tests"], int, "dv plan report.summary.total_tests")
    require_type(summary["total_assertions"], int, "dv plan report.summary.total_assertions")
    require_type(summary["total_coverage_items"], int, "dv plan report.summary.total_coverage_items")
    require_type(summary["total_risks"], int, "dv plan report.summary.total_risks")
    require_type(summary["total_unresolved"], int, "dv plan report.summary.total_unresolved")


def validate_cdc_report(data: dict) -> None:
    require_type(data, dict, "cdc report")
    require_keys(data, ["module", "file", "clock_domains", "crossings", "summary"], "cdc report")

    require_type(data["module"], str, "cdc report.module")
    require_type(data["file"], str, "cdc report.file")
    require_type(data["clock_domains"], list, "cdc report.clock_domains")
    require_type(data["crossings"], list, "cdc report.crossings")
    require_type(data["summary"], dict, "cdc report.summary")

    for index, item in enumerate(data["clock_domains"], start=1):
        context = f"cdc report.clock_domains[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["name"], context)
        require_type(item["name"], str, f"{context}.name")

    valid_methods = {
        "2ff",
        "3ff",
        "gray",
        "handshake",
        "toggle_snapshot",
        "async_fifo",
        "pulse_sync",
        "none",
    }
    valid_severities = {"critical", "high", "medium", "low", "info"}

    for index, item in enumerate(data["crossings"], start=1):
        context = f"cdc report.crossings[{index}]"
        require_type(item, dict, context)
        require_keys(
            item,
            [
                "id",
                "signal",
                "width",
                "source_domain",
                "dest_domain",
                "line",
                "direction",
                "synchronized",
                "sync_method",
                "severity",
                "description",
            ],
            context,
        )
        if not CDC_ID_RE.match(item["id"]):
            raise ValidationError(f"{context}.id must match CDC-NNN")
        require_type(item["signal"], str, f"{context}.signal")
        require_type(item["width"], int, f"{context}.width")
        require_type(item["source_domain"], str, f"{context}.source_domain")
        require_type(item["dest_domain"], str, f"{context}.dest_domain")
        validate_line_field(item["line"], f"{context}.line")
        require_type(item["direction"], str, f"{context}.direction")
        require_type(item["synchronized"], bool, f"{context}.synchronized")
        if item["sync_method"] not in valid_methods:
            raise ValidationError(f"{context}.sync_method is invalid")
        if item["severity"] not in valid_severities:
            raise ValidationError(f"{context}.severity is invalid")
        require_type(item["description"], str, f"{context}.description")
        if "fix" in item:
            require_type(item["fix"], str, f"{context}.fix")

    summary = data["summary"]
    require_keys(summary, ["total_crossings", "violations", "by_severity"], "cdc report.summary")
    require_type(summary["total_crossings"], int, "cdc report.summary.total_crossings")
    require_type(summary["violations"], int, "cdc report.summary.violations")
    require_type(summary["by_severity"], dict, "cdc report.summary.by_severity")
    require_keys(
        summary["by_severity"],
        ["critical", "high", "medium", "low", "info"],
        "cdc report.summary.by_severity",
    )
    for key, value in summary["by_severity"].items():
        require_type(value, int, f"cdc report.summary.by_severity.{key}")


def validate_timing_report(data: dict) -> None:
    require_type(data, dict, "timing report")
    require_keys(
        data,
        ["module", "file", "config", "registers", "paths", "unresolved", "summary"],
        "timing report",
    )

    require_type(data["module"], str, "timing report.module")
    require_type(data["file"], str, "timing report.file")
    require_type(data["config"], str, "timing report.config")
    require_type(data["registers"], list, "timing report.registers")
    require_type(data["paths"], list, "timing report.paths")
    require_type(data["unresolved"], list, "timing report.unresolved")
    require_type(data["summary"], dict, "timing report.summary")

    valid_sources = {"always_ff", "macro", "library_cell", "inferred"}
    valid_difficulties = {"critical", "hard", "moderate", "easy"}

    for index, item in enumerate(data["registers"], start=1):
        context = f"timing report.registers[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["name", "width", "clock", "source", "line"], context)
        require_type(item["name"], str, f"{context}.name")
        require_type(item["width"], int, f"{context}.width")
        require_type(item["clock"], str, f"{context}.clock")
        if item["source"] not in valid_sources:
            raise ValidationError(f"{context}.source is invalid")
        require_type(item["line"], int, f"{context}.line")

    for index, item in enumerate(data["paths"], start=1):
        context = f"timing report.paths[{index}]"
        require_type(item, dict, context)
        require_keys(
            item,
            ["id", "from", "to", "depth", "difficulty", "stages", "crosses_module", "description"],
            context,
        )
        if not PATH_ID_RE.match(item["id"]):
            raise ValidationError(f"{context}.id must match PATH-NNN")
        require_type(item["from"], str, f"{context}.from")
        require_type(item["to"], str, f"{context}.to")
        require_type(item["depth"], int, f"{context}.depth")
        if item["difficulty"] not in valid_difficulties:
            raise ValidationError(f"{context}.difficulty is invalid")
        require_type(item["stages"], list, f"{context}.stages")
        require_type(item["crosses_module"], bool, f"{context}.crosses_module")
        require_type(item["description"], str, f"{context}.description")
        if "module_path" in item:
            require_type(item["module_path"], list, f"{context}.module_path")
            if not all(isinstance(part, str) for part in item["module_path"]):
                raise ValidationError(f"{context}.module_path must contain only strings")
        if "suggestion" in item:
            require_type(item["suggestion"], str, f"{context}.suggestion")

        for stage_index, stage in enumerate(item["stages"], start=1):
            stage_context = f"{context}.stages[{stage_index}]"
            require_type(stage, dict, stage_context)
            require_keys(stage, ["op", "width", "depth", "line"], stage_context)
            require_type(stage["op"], str, f"{stage_context}.op")
            require_type(stage["width"], int, f"{stage_context}.width")
            require_type(stage["depth"], int, f"{stage_context}.depth")
            require_type(stage["line"], int, f"{stage_context}.line")

    for index, item in enumerate(data["unresolved"], start=1):
        context = f"timing report.unresolved[{index}]"
        require_type(item, dict, context)
        require_keys(item, ["name", "line", "reason"], context)
        require_type(item["name"], str, f"{context}.name")
        require_type(item["line"], int, f"{context}.line")
        require_type(item["reason"], str, f"{context}.reason")

    summary = data["summary"]
    require_keys(
        summary,
        ["total_registers", "total_paths", "by_difficulty", "deepest_path"],
        "timing report.summary",
    )
    require_type(summary["total_registers"], int, "timing report.summary.total_registers")
    require_type(summary["total_paths"], int, "timing report.summary.total_paths")
    require_type(summary["by_difficulty"], dict, "timing report.summary.by_difficulty")
    require_keys(
        summary["by_difficulty"],
        ["critical", "hard", "moderate", "easy"],
        "timing report.summary.by_difficulty",
    )
    for key, value in summary["by_difficulty"].items():
        require_type(value, int, f"timing report.summary.by_difficulty.{key}")

    deepest = summary["deepest_path"]
    require_type(deepest, dict, "timing report.summary.deepest_path")
    require_keys(deepest, ["id", "depth", "from", "to"], "timing report.summary.deepest_path")
    require_type(deepest["id"], str, "timing report.summary.deepest_path.id")
    require_type(deepest["depth"], int, "timing report.summary.deepest_path.depth")
    require_type(deepest["from"], str, "timing report.summary.deepest_path.from")
    require_type(deepest["to"], str, "timing report.summary.deepest_path.to")


def validate_block_design_context(
    design: dict,
    context: str,
    *,
    require_brief_summary: bool = False,
    require_existing_rtl_files: bool = False,
    require_rtl_files: bool = False,
) -> None:
    require_type(design, dict, context)
    require_keys(design, ["top_module"], context)
    require_type(design["top_module"], str, f"{context}.top_module")
    if require_brief_summary:
        require_keys(design, ["brief_summary"], context)
        require_type(design["brief_summary"], str, f"{context}.brief_summary")
    if require_existing_rtl_files:
        require_keys(design, ["existing_rtl_files"], context)
        require_string_list(
            design["existing_rtl_files"],
            f"{context}.existing_rtl_files",
        )
    if require_rtl_files:
        require_keys(design, ["rtl_files"], context)
        require_string_list(design["rtl_files"], f"{context}.rtl_files", allow_empty=False)


def validate_requirement_ids(value: list, context: str) -> None:
    require_string_list(value, context)
    for item in value:
        if not REQ_ID_RE.match(item):
            raise ValidationError(f"{context} contains an invalid requirement id: {item}")


def validate_requirements_list(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_priority = {"must", "should", "could"}
    valid_source = {"user", "rtl", "both"}
    valid_category = {
        "function",
        "interface",
        "clock_reset",
        "performance",
        "power",
        "area",
        "testability",
    }
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(
            item,
            ["id", "title", "category", "priority", "source", "description", "acceptance_criteria"],
            item_context,
        )
        if not REQ_ID_RE.match(item["id"]):
            raise ValidationError(f"{item_context}.id must match REQ-NNN")
        require_type(item["title"], str, f"{item_context}.title")
        require_enum(item["category"], valid_category, f"{item_context}.category")
        require_enum(item["priority"], valid_priority, f"{item_context}.priority")
        require_enum(item["source"], valid_source, f"{item_context}.source")
        require_type(item["description"], str, f"{item_context}.description")
        require_type(item["acceptance_criteria"], str, f"{item_context}.acceptance_criteria")


def validate_ppa_targets(value: dict, context: str) -> None:
    require_type(value, dict, context)
    require_keys(value, ["performance", "power", "area"], context)
    valid_status = {"numeric", "qualitative", "missing"}
    for key in ("performance", "power", "area"):
        item_context = f"{context}.{key}"
        item = value[key]
        require_type(item, dict, item_context)
        require_keys(item, ["target", "units", "priority", "status"], item_context)
        require_optional_type(item["target"], str, f"{item_context}.target")
        require_optional_type(item["units"], str, f"{item_context}.units")
        require_type(item["priority"], str, f"{item_context}.priority")
        require_enum(item["status"], valid_status, f"{item_context}.status")


def validate_open_questions(value: list, context: str) -> None:
    require_type(value, list, context)
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["topic", "question", "blocking"], item_context)
        require_type(item["topic"], str, f"{item_context}.topic")
        require_type(item["question"], str, f"{item_context}.question")
        require_type(item["blocking"], bool, f"{item_context}.blocking")
        if "related_requirement_ids" in item:
            validate_requirement_ids(item["related_requirement_ids"], f"{item_context}.related_requirement_ids")


def validate_generic_unresolved(value: list, context: str) -> None:
    require_type(value, list, context)
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["item", "reason", "blocking"], item_context)
        require_type(item["item"], str, f"{item_context}.item")
        require_type(item["reason"], str, f"{item_context}.reason")
        require_type(item["blocking"], bool, f"{item_context}.blocking")
        if "requirement_ids" in item:
            validate_requirement_ids(item["requirement_ids"], f"{item_context}.requirement_ids")
        if "related_ids" in item:
            require_string_list(item["related_ids"], f"{item_context}.related_ids")


def validate_block_requirements(data: dict) -> None:
    require_type(data, dict, "block requirements report")
    require_keys(
        data,
        ["design", "requirements", "ppa_targets", "open_questions", "summary"],
        "block requirements report",
    )
    validate_block_design_context(
        data["design"],
        "block requirements report.design",
        require_brief_summary=True,
    )
    validate_requirements_list(data["requirements"], "block requirements report.requirements")
    validate_ppa_targets(data["ppa_targets"], "block requirements report.ppa_targets")
    validate_open_questions(data["open_questions"], "block requirements report.open_questions")

    summary = data["summary"]
    require_type(summary, dict, "block requirements report.summary")
    require_keys(
        summary,
        ["total_requirements", "total_open_questions", "ppa_complete"],
        "block requirements report.summary",
    )
    require_type(summary["total_requirements"], int, "block requirements report.summary.total_requirements")
    require_type(summary["total_open_questions"], int, "block requirements report.summary.total_open_questions")
    require_type(summary["ppa_complete"], bool, "block requirements report.summary.ppa_complete")


def validate_requirements_trace(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_coverage = {"full", "partial"}
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["requirement_id", "spec_sections", "coverage"], item_context)
        if not REQ_ID_RE.match(item["requirement_id"]):
            raise ValidationError(f"{item_context}.requirement_id must match REQ-NNN")
        require_string_list(item["spec_sections"], f"{item_context}.spec_sections", allow_empty=False)
        require_enum(item["coverage"], valid_coverage, f"{item_context}.coverage")


def validate_spec_artifact(value: dict, context: str) -> None:
    require_type(value, dict, context)
    require_keys(value, ["path", "format"], context)
    require_type(value["path"], str, f"{context}.path")
    require_enum(value["format"], {"markdown"}, f"{context}.format")


def validate_diagrams(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_tools = {"wavedrom", "mermaid", "blockdiag"}
    valid_purpose = {"timing", "state_machine", "block_diagram"}
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["tool", "title", "purpose", "artifact_path", "content"], item_context)
        require_enum(item["tool"], valid_tools, f"{item_context}.tool")
        require_type(item["title"], str, f"{item_context}.title")
        require_enum(item["purpose"], valid_purpose, f"{item_context}.purpose")
        require_type(item["artifact_path"], str, f"{item_context}.artifact_path")
        require_type(item["content"], str, f"{item_context}.content")


def validate_microarchitecture_spec(data: dict) -> None:
    require_type(data, dict, "microarchitecture spec report")
    require_keys(
        data,
        ["design", "requirements_trace", "artifact", "spec_markdown", "diagrams", "unresolved", "summary"],
        "microarchitecture spec report",
    )
    validate_block_design_context(
        data["design"],
        "microarchitecture spec report.design",
        require_brief_summary=True,
    )
    validate_requirements_trace(data["requirements_trace"], "microarchitecture spec report.requirements_trace")
    validate_spec_artifact(data["artifact"], "microarchitecture spec report.artifact")
    require_type(data["spec_markdown"], str, "microarchitecture spec report.spec_markdown")
    validate_diagrams(data["diagrams"], "microarchitecture spec report.diagrams")
    validate_generic_unresolved(data["unresolved"], "microarchitecture spec report.unresolved")

    summary = data["summary"]
    require_type(summary, dict, "microarchitecture spec report.summary")
    require_keys(
        summary,
        ["total_traced_requirements", "total_diagrams", "total_unresolved"],
        "microarchitecture spec report.summary",
    )
    require_type(
        summary["total_traced_requirements"],
        int,
        "microarchitecture spec report.summary.total_traced_requirements",
    )
    require_type(summary["total_diagrams"], int, "microarchitecture spec report.summary.total_diagrams")
    require_type(summary["total_unresolved"], int, "microarchitecture spec report.summary.total_unresolved")


def validate_rtl_source_files(value: list, context: str) -> None:
    require_type(value, list, context)
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["path", "module", "language", "content"], item_context)
        require_type(item["path"], str, f"{item_context}.path")
        require_type(item["module"], str, f"{item_context}.module")
        require_enum(item["language"], {"systemverilog"}, f"{item_context}.language")
        require_type(item["content"], str, f"{item_context}.content")


def validate_rtl_modules(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_role = {"top", "datapath", "control", "interface", "support"}
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["name", "role", "clocks", "resets", "description"], item_context)
        require_type(item["name"], str, f"{item_context}.name")
        require_enum(item["role"], valid_role, f"{item_context}.role")
        require_string_list(item["clocks"], f"{item_context}.clocks", allow_empty=False)
        require_string_list(item["resets"], f"{item_context}.resets")
        require_type(item["description"], str, f"{item_context}.description")


def validate_rtl_traceability(value: list, context: str) -> None:
    require_type(value, list, context)
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["requirement_id", "spec_sections", "rtl_files", "rtl_signals"], item_context)
        if not REQ_ID_RE.match(item["requirement_id"]):
            raise ValidationError(f"{item_context}.requirement_id must match REQ-NNN")
        require_string_list(item["spec_sections"], f"{item_context}.spec_sections", allow_empty=False)
        require_string_list(item["rtl_files"], f"{item_context}.rtl_files", allow_empty=False)
        require_string_list(item["rtl_signals"], f"{item_context}.rtl_signals")


def validate_tool_evidence(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_status = {"used", "unavailable", "incomplete", "error"}
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["source", "tools", "purpose", "status", "summary"], item_context)
        require_type(item["source"], str, f"{item_context}.source")
        require_string_list(item["tools"], f"{item_context}.tools")
        require_type(item["purpose"], str, f"{item_context}.purpose")
        require_enum(item["status"], valid_status, f"{item_context}.status")
        require_type(item["summary"], str, f"{item_context}.summary")


def validate_rtl_design(data: dict) -> None:
    require_type(data, dict, "rtl design report")
    require_keys(
        data,
        ["design", "source_files", "rtl_modules", "traceability", "unresolved", "tool_evidence", "summary"],
        "rtl design report",
    )
    validate_block_design_context(
        data["design"],
        "rtl design report.design",
        require_brief_summary=True,
    )
    validate_rtl_source_files(data["source_files"], "rtl design report.source_files")
    validate_rtl_modules(data["rtl_modules"], "rtl design report.rtl_modules")
    validate_rtl_traceability(data["traceability"], "rtl design report.traceability")
    validate_generic_unresolved(data["unresolved"], "rtl design report.unresolved")
    validate_tool_evidence(data["tool_evidence"], "rtl design report.tool_evidence")

    summary = data["summary"]
    require_type(summary, dict, "rtl design report.summary")
    require_keys(
        summary,
        ["total_source_files", "total_modules", "total_trace_links", "total_unresolved"],
        "rtl design report.summary",
    )
    require_type(summary["total_source_files"], int, "rtl design report.summary.total_source_files")
    require_type(summary["total_modules"], int, "rtl design report.summary.total_modules")
    require_type(summary["total_trace_links"], int, "rtl design report.summary.total_trace_links")
    require_type(summary["total_unresolved"], int, "rtl design report.summary.total_unresolved")


def validate_lint_findings(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_severity = {"critical", "high", "medium", "low", "info"}
    valid_category = {"synthesizability", "latch", "reset", "width", "cdc_structure", "style"}
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(
            item,
            ["id", "severity", "category", "file", "line", "message", "blocking"],
            item_context,
        )
        if not LINT_ID_RE.match(item["id"]):
            raise ValidationError(f"{item_context}.id must match LINT-NNN")
        require_enum(item["severity"], valid_severity, f"{item_context}.severity")
        require_enum(item["category"], valid_category, f"{item_context}.category")
        require_type(item["file"], str, f"{item_context}.file")
        require_type(item["line"], int, f"{item_context}.line")
        require_type(item["message"], str, f"{item_context}.message")
        require_type(item["blocking"], bool, f"{item_context}.blocking")
        if "recommendation" in item:
            require_type(item["recommendation"], str, f"{item_context}.recommendation")


def validate_rtl_lint_report(data: dict) -> None:
    require_type(data, dict, "rtl lint report")
    require_keys(data, ["design", "findings", "tool_evidence", "summary"], "rtl lint report")
    validate_block_design_context(
        data["design"],
        "rtl lint report.design",
        require_rtl_files=True,
    )
    validate_lint_findings(data["findings"], "rtl lint report.findings")
    validate_tool_evidence(data["tool_evidence"], "rtl lint report.tool_evidence")

    summary = data["summary"]
    require_type(summary, dict, "rtl lint report.summary")
    require_keys(
        summary,
        ["total_findings", "blocking_findings", "by_severity"],
        "rtl lint report.summary",
    )
    require_type(summary["total_findings"], int, "rtl lint report.summary.total_findings")
    require_type(summary["blocking_findings"], int, "rtl lint report.summary.blocking_findings")
    require_type(summary["by_severity"], dict, "rtl lint report.summary.by_severity")
    require_keys(
        summary["by_severity"],
        ["critical", "high", "medium", "low", "info"],
        "rtl lint report.summary.by_severity",
    )
    for key, value in summary["by_severity"].items():
        require_type(value, int, f"rtl lint report.summary.by_severity.{key}")


def validate_reset_domains(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_active = {"active_high", "active_low"}
    valid_style = {"sync", "async"}
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(item, ["name", "active", "style", "line"], item_context)
        require_type(item["name"], str, f"{item_context}.name")
        require_enum(item["active"], valid_active, f"{item_context}.active")
        require_enum(item["style"], valid_style, f"{item_context}.style")
        require_type(item["line"], int, f"{item_context}.line")


def validate_rdc_crossings(value: list, context: str) -> None:
    require_type(value, list, context)
    valid_severity = {"critical", "high", "medium", "low", "info"}
    for index, item in enumerate(value, start=1):
        item_context = f"{context}[{index}]"
        require_type(item, dict, item_context)
        require_keys(
            item,
            ["id", "signal", "source_reset", "dest_reset", "line", "protected", "severity", "description"],
            item_context,
        )
        if not RDC_ID_RE.match(item["id"]):
            raise ValidationError(f"{item_context}.id must match RDC-NNN")
        require_type(item["signal"], str, f"{item_context}.signal")
        require_type(item["source_reset"], str, f"{item_context}.source_reset")
        require_type(item["dest_reset"], str, f"{item_context}.dest_reset")
        require_type(item["line"], int, f"{item_context}.line")
        require_type(item["protected"], bool, f"{item_context}.protected")
        require_enum(item["severity"], valid_severity, f"{item_context}.severity")
        require_type(item["description"], str, f"{item_context}.description")
        if "fix" in item:
            require_type(item["fix"], str, f"{item_context}.fix")


def validate_rdc_report(data: dict) -> None:
    require_type(data, dict, "rdc report")
    require_keys(data, ["design", "reset_domains", "crossings", "summary"], "rdc report")
    validate_block_design_context(
        data["design"],
        "rdc report.design",
        require_rtl_files=True,
    )
    validate_reset_domains(data["reset_domains"], "rdc report.reset_domains")
    validate_rdc_crossings(data["crossings"], "rdc report.crossings")

    summary = data["summary"]
    require_type(summary, dict, "rdc report.summary")
    require_keys(summary, ["total_crossings", "violations", "by_severity"], "rdc report.summary")
    require_type(summary["total_crossings"], int, "rdc report.summary.total_crossings")
    require_type(summary["violations"], int, "rdc report.summary.violations")
    require_type(summary["by_severity"], dict, "rdc report.summary.by_severity")
    require_keys(
        summary["by_severity"],
        ["critical", "high", "medium", "low", "info"],
        "rdc report.summary.by_severity",
    )
    for key, value in summary["by_severity"].items():
        require_type(value, int, f"rdc report.summary.by_severity.{key}")


def validate_package_spec(value: dict, context: str) -> None:
    require_type(value, dict, context)
    require_keys(value, ["artifact_path", "requirements_trace", "diagrams"], context)
    require_type(value["artifact_path"], str, f"{context}.artifact_path")
    validate_requirements_trace(value["requirements_trace"], f"{context}.requirements_trace")
    validate_diagrams(value["diagrams"], f"{context}.diagrams")


def validate_package_rtl(value: dict, context: str) -> None:
    require_type(value, dict, context)
    require_keys(value, ["source_files", "rtl_modules", "traceability"], context)
    validate_rtl_source_files(value["source_files"], f"{context}.source_files")
    validate_rtl_modules(value["rtl_modules"], f"{context}.rtl_modules")
    validate_rtl_traceability(value["traceability"], f"{context}.traceability")


def validate_audit_summary(value: dict, context: str) -> None:
    require_type(value, dict, context)
    require_keys(value, ["lint", "cdc", "rdc", "timing", "ready_for_dv_handoff"], context)
    require_type(value["ready_for_dv_handoff"], bool, f"{context}.ready_for_dv_handoff")

    lint = value["lint"]
    require_type(lint, dict, f"{context}.lint")
    require_keys(lint, ["total_findings", "blocking_findings"], f"{context}.lint")
    require_type(lint["total_findings"], int, f"{context}.lint.total_findings")
    require_type(lint["blocking_findings"], int, f"{context}.lint.blocking_findings")

    for name in ("cdc", "rdc"):
        section = value[name]
        section_context = f"{context}.{name}"
        require_type(section, dict, section_context)
        require_keys(section, ["violations", "highest_severity"], section_context)
        require_type(section["violations"], int, f"{section_context}.violations")
        require_enum(
            section["highest_severity"],
            {"critical", "high", "medium", "low", "info", "none"},
            f"{section_context}.highest_severity",
        )

    timing = value["timing"]
    require_type(timing, dict, f"{context}.timing")
    require_keys(timing, ["hard_or_worse_paths", "deepest_path_depth"], f"{context}.timing")
    require_type(timing["hard_or_worse_paths"], int, f"{context}.timing.hard_or_worse_paths")
    require_type(timing["deepest_path_depth"], int, f"{context}.timing.deepest_path_depth")


def validate_downstream_handoff(value: dict, context: str) -> None:
    require_type(value, dict, context)
    require_keys(
        value,
        ["recommended_flow", "top_module", "rtl_files", "design_intent_markdown", "notes"],
        context,
    )
    require_enum(value["recommended_flow"], {"block-dv-plan"}, f"{context}.recommended_flow")
    require_type(value["top_module"], str, f"{context}.top_module")
    require_string_list(value["rtl_files"], f"{context}.rtl_files", allow_empty=False)
    require_type(value["design_intent_markdown"], str, f"{context}.design_intent_markdown")
    require_type(value["notes"], str, f"{context}.notes")


def validate_block_rtl_package(data: dict) -> None:
    require_type(data, dict, "block rtl package report")
    require_keys(
        data,
        [
            "design",
            "requirements",
            "ppa_targets",
            "spec",
            "rtl",
            "audit_summary",
            "unresolved",
            "downstream_handoff",
            "summary",
        ],
        "block rtl package report",
    )
    validate_block_design_context(
        data["design"],
        "block rtl package report.design",
        require_brief_summary=True,
        require_rtl_files=True,
    )
    validate_requirements_list(data["requirements"], "block rtl package report.requirements")
    validate_ppa_targets(data["ppa_targets"], "block rtl package report.ppa_targets")
    validate_package_spec(data["spec"], "block rtl package report.spec")
    validate_package_rtl(data["rtl"], "block rtl package report.rtl")
    validate_audit_summary(data["audit_summary"], "block rtl package report.audit_summary")
    validate_generic_unresolved(data["unresolved"], "block rtl package report.unresolved")
    validate_downstream_handoff(data["downstream_handoff"], "block rtl package report.downstream_handoff")

    summary = data["summary"]
    require_type(summary, dict, "block rtl package report.summary")
    require_keys(
        summary,
        ["total_requirements", "total_rtl_files", "total_blocking_issues", "total_unresolved"],
        "block rtl package report.summary",
    )
    require_type(summary["total_requirements"], int, "block rtl package report.summary.total_requirements")
    require_type(summary["total_rtl_files"], int, "block rtl package report.summary.total_rtl_files")
    require_type(summary["total_blocking_issues"], int, "block rtl package report.summary.total_blocking_issues")
    require_type(summary["total_unresolved"], int, "block rtl package report.summary.total_unresolved")
