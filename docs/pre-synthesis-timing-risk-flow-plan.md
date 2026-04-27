# Pre-Synthesis Timing Risk Flow Plan

## Goal

Create an agentic pre-synthesis timing-risk flow that can start from HDL source
or an existing textual design view and end with actionable timing feedback before
any synthesis or STA run.

The flow should support Verilog, SystemVerilog, VHDL, and proprietary hardware
description languages by separating design-view extraction from timing analysis.

## Scope Split

The implementation is split across one flow and two focused skills.

### `hdl-design-view-extractor`

Purpose:

- convert HDL source, UHDM text, AST JSON, MCP output, or model reasoning into a
  source-grounded textual design view
- preserve line evidence, tool provenance, confidence, and unresolved structure
- avoid timing, CDC, RDC, synthesis, or verification conclusions

Preferred textual design-view order:

1. UHDM textual view
2. AST/CST JSON, such as slang or pyslang output
3. MCP or tool-provided textual AST, elaborated tree, or design graph
4. model-derived design view from raw source text

### `rtl-timing-analyzer`

Purpose:

- consume an existing textual design view or small visible RTL block
- identify timing endpoints and reg-to-reg or boundary timing paths
- estimate combinational depth with the configured model
- classify timing risk and emit source-grounded optimization guidance

It should not choose parsers, run MCP tools, produce UHDM, dump AST JSON, or
normalize unknown source languages.

### `pre-synthesis-timing-risk`

Purpose:

- orchestrate source inspection, design-view extraction, focused timing analysis,
  unresolved-object handling, and final handoff

This flow is the right place for agentic decisions such as:

- whether source is already a design view
- whether to prefer UHDM or AST JSON
- whether an MCP/tool view is needed
- whether model-derived extraction is acceptable
- whether missing hierarchy blocks timing analysis

## Repository Changes

Implemented artifacts:

- `skills/hdl-design-view-extractor/SKILL.md`
- `skills/rtl-timing-analyzer/SKILL.md`
- `flows/pre-synthesis-timing-risk/FLOW.md`
- `schemas/hdl-design-view.schema.json`
- `datasets/fixtures/hdl-design-view/`
- `evals/smoke/hdl-design-view-extractor/`
- `evals/smoke/rtl-timing-analyzer/`
- `evals/smoke-flows/pre-synthesis-timing-risk/`
- `schemas/pre-synthesis-timing-risk.schema.json`
- `scripts/check_flow_smoke.py`

The old `rtl-timing-path-analyzer` slug has been replaced by
`rtl-timing-analyzer` across repo references.

## Acceptance Criteria

The split is working when:

- design-view extraction has its own isolated fixtures and smoke cases
- timing analysis remains focused on analyzing existing structure
- the full flow composes extraction plus timing analysis
- a flow smoke case validates RTL input, intermediate design-view and timing
  artifacts, and a final timing-risk handoff
- SystemVerilog/Verilog can use source, UHDM text, or AST JSON views
- VHDL and proprietary languages can use textual MCP/tool views or
  confidence-limited model-derived views
- every finding remains source-grounded and explicit about unresolved structure
- smoke validation passes without live model execution

## Residual Limits

This flow remains pre-synthesis. It cannot replace synthesis, STA, SDC review,
gate-level netlist analysis, clock-tree analysis, placement, routing, or signoff
timing closure.
