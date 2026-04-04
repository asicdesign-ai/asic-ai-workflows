#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from pathlib import Path


CDC_ID_RE = re.compile(r"^CDC-\d{3}$")
PATH_ID_RE = re.compile(r"^PATH-\d{3}$")
OBJ_ID_RE = re.compile(r"^OBJ-\d{3}$")
BEH_ID_RE = re.compile(r"^BEH-\d{3}$")
TEST_ID_RE = re.compile(r"^TEST-\d{3}$")
SVA_ID_RE = re.compile(r"^SVA-\d{3}$")
COV_ID_RE = re.compile(r"^COV-\d{3}$")
RISK_ID_RE = re.compile(r"^RISK-\d{3}$")
UNR_ID_RE = re.compile(r"^UNR-\d{3}$")


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
