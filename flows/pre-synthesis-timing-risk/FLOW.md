---
name: pre-synthesis-timing-risk
description: >
  Orchestrate pre-synthesis timing-risk analysis from HDL source or existing
  textual design views. Use this flow when the user wants agentic handling of
  Verilog, SystemVerilog, VHDL, or proprietary HDL before synthesis: choose or
  request an AI-readable design view, extract timing-relevant structure, run the
  RTL timing analyzer, and assemble a source-grounded timing-risk handoff.
---

# Pre-Synthesis Timing Risk Flow

Convert HDL source or parser output into an AI-readable design view, analyze
structural timing risk, and report actionable pre-synthesis feedback without
claiming STA or signoff timing.

## Inputs

- `top_module` or top design unit
- one or more HDL source files, filelists, UHDM text dumps, AST JSON files, or
  MCP/tool design-view artifacts
- optional `source_language`
- optional `timing_config`
- optional `target_clock_period` for context only
- optional `known_missing_hierarchy`

## Rules

Apply these repo rules across the flow:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/common/tool-evidence-provenance.md`
- `../../rules/timing/register-evidence.md`

## Skills

Run these skills in order:

1. `../../skills/hdl-design-view-extractor/SKILL.md`
2. `../../skills/rtl-timing-analyzer/SKILL.md`

## Execution

1. Inspect the input artifact types and source language.
2. If a UHDM text dump or parser AST JSON is already provided, treat it as the
   design-view input and preserve tool provenance.
3. If only HDL source is provided, run `hdl-design-view-extractor` to create a
   source-grounded textual design view. Prefer UHDM text, then AST JSON, then
   tool design graph, then model-derived view.
4. If the source language is VHDL or proprietary and no parser/MCP/tool view is
   available, allow a model-derived design view only when every structural claim
   carries evidence and confidence.
5. Run `rtl-timing-analyzer` on the extracted or provided design view.
6. Do not let the timing analyzer choose or run extraction tools; extraction
   remains a flow-level responsibility.
7. Preserve unresolved hierarchy, unknown cells, unknown language constructs, and
   missing timing exceptions as unresolved flow items.
8. Assemble one YAML handoff that includes the design-view summary, timing
   summary, ranked risks, recommended next actions, and residual limits.

## Output Format

Produce a single YAML document:

```yaml
flow:
  name: pre-synthesis-timing-risk
  top_unit: simple_counter
  source_language: systemverilog

design_view:
  artifact: artifacts/design-views/simple_counter.view.json
  view_format: model_derived
  confidence: high
  sequential_elements: 1
  combinational_nodes: 2
  unresolved: 0

timing:
  report: artifacts/timing/simple_counter_timing.yaml
  total_paths: 1
  hard_or_worse_paths: 0
  deepest_path:
    id: PATH-001
    depth: 4
    from: count_q
    to: count_q

ranked_risks:
  - id: RISK-001
    source: timing_report
    severity: moderate
    description: "The counter feedback path contains an incrementer and mux before count_q."
    evidence:
      design_view_node: COMB-001
      timing_path: PATH-001

recommended_actions:
  - "Review hard or critical paths before synthesis."
  - "Provide missing submodule source or a UHDM/AST design view for unresolved hierarchy."

unresolved: []

summary:
  design_view_ready: true
  timing_report_ready: true
  requires_synthesis_or_sta: false
  total_unresolved: 0
```

## Scope Limitations

- Can do: orchestrate extraction and structural timing-risk analysis before
  synthesis.
- Cannot do: produce real slack, run signoff STA, infer false paths or
  multicycle paths without constraints, or guarantee that synthesis will preserve
  the same critical path ordering.
