---
name: rtl-lint-auditor
description: >
  Review synthesizable SystemVerilog for static RTL issues such as inferred
  latches, reset mismatches, width hazards, and multi-driver structure. Use this
  skill whenever generated RTL needs a deterministic front-end lint audit before
  CDC, RDC, or timing review.
---

# RTL Lint Auditor Skill

Audit block-level SystemVerilog for front-end lint issues and emit one
deterministic finding report.

Scope: block or small IP. This is a static lint audit, not an EDA signoff run.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/common/tool-evidence-provenance.md`
- `../../rules/rtl/synthesizable-systemverilog.md`
- `../../rules/rtl/lint-severity.md`

## Analysis

Read the RTL and perform these steps:

1. If `project_root`, source files, or a filelist are provided and HDL/EDA MCP
   tools are available, collect read-only compiler or lint evidence before
   finalizing findings.
2. Identify structural lint issues that can be proven from the provided RTL text
   or tool evidence.
3. Classify each issue with the severity mapping in
   `../../rules/rtl/lint-severity.md`.
4. Mark `critical` and `high` findings as blocking.
5. Suggest the smallest valid fix for blocking issues.
6. Emit an empty `findings` list when the RTL is clean under this rule set.

## Optional MCP Evidence Intake

When MCP tools are available, use them as evidence sources before finalizing
findings. Discover tools by schema and description, not by vendor name. Prefer
read-only HDL/EDA tools that provide parse/elaboration diagnostics, design-unit
inventory, hierarchy, symbol lookup, or lint-rule-deck reports.

`pyslang-mcp` can ground front-end diagnostics, module descriptions, hierarchy,
and symbol references. Useful calls include `pyslang_parse_filelist` or
`pyslang_parse_files`, `pyslang_get_diagnostics`,
`pyslang_list_design_units`, `pyslang_describe_design_unit`,
`pyslang_get_hierarchy`, and `pyslang_find_symbol`. Treat
`pyslang-mcp` as compiler-backed context, not as a replacement for a full lint
deck.

For vendor or internal EDA MCPs, use tools only when their schema clearly exposes
read-only parse/elaboration diagnostics, lint report retrieval, design-unit or
hierarchy queries, symbol lookup, or waiver/status lookup that is explicitly in
scope. Do not assume public vendor MCP support or hard-code tool names.

Normalize every tool finding into this skill's deterministic YAML severity model.
Do not blindly copy vendor severities when they conflict with
`../../rules/rtl/lint-severity.md`; preserve original tool rule IDs, severities,
or diagnostics only as evidence metadata.

Do not claim lint cleanliness solely because `pyslang-mcp` returns zero
diagnostics. That means the design parsed under that frontend; text-grounded lint
hazards can still remain.

If MCP evidence is unavailable, incomplete, or returns a structured tool error,
continue with text-grounded analysis and record the limitation in
`tool_evidence` when a tool path was attempted. Emit `tool_evidence: []` when no
MCP evidence was used. When tool evidence is present, each entry must contain
`source`, `tools`, `purpose`, `status`, and `summary`. Do not invoke destructive,
synthesis, simulation, CDC, timing, or RTL-editing tools from this skill.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: event_counter
  rtl_files:
    - rtl/event_counter.sv

findings:
  - id: LINT-001
    severity: high
    category: latch
    file: rtl/event_counter.sv
    line: 27
    message: "The combinational next-state block leaves irq_nxt unassigned on one branch."
    recommendation: "Assign irq_nxt on every path or provide a default assignment before the branch tree."
    blocking: true

tool_evidence: []

summary:
  total_findings: 1
  blocking_findings: 1
  by_severity:
    critical: 0
    high: 1
    medium: 0
    low: 0
    info: 0
```

## Scope Limitations

- **Can do**: flag code-local lint hazards grounded in the RTL text.
- **Cannot do**: replace full lint tool rule decks, prove CDC safety, or prove
  implementation timing.
