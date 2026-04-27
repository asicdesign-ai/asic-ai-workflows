---
name: rtl-timing-analyzer
description: >
  Analyze an HDL design view or visible RTL for pre-synthesis timing risk by
  estimating combinational logic depth on register-to-register and boundary
  timing paths. Use this skill when the user already has a UHDM text dump, AST
  JSON, source-grounded textual design view, or small visible RTL block and asks
  for critical paths, deep combinational logic, reg-to-reg timing risk, or
  pre-synthesis timing feedback. This skill is analysis-only; use an
  HDL-design-view extraction skill or flow when parser/tool/MCP selection,
  source-language normalization, or design-view generation is required.
---

# RTL Timing Analyzer Skill

Estimate combinational depth and structural timing risk from an already visible
design representation. Produce a ranked YAML report of timing paths ordered by
difficulty. The deepest paths are likely candidates for pre-synthesis timing
review, but this report is not STA and must not claim real slack or signoff
closure.

This skill is intentionally focused. It analyzes timing structure; it does not
choose parsers, run MCP tools, create UHDM dumps, generate AST JSON, or normalize
unknown HDL languages. Use `../../skills/hdl-design-view-extractor/SKILL.md` or
a flow when those steps are needed.

## Inputs

Accept one or more of:

- a UHDM textual dump
- parser-provided AST/CST JSON, such as slang or pyslang output
- a source-grounded textual design view from another tool or model pass
- a small Verilog/SystemVerilog RTL block that is fully visible in the prompt
- optional original RTL files for source-line evidence lookup
- optional timing configuration YAML

If the input is a large raw HDL project, an unknown language, missing hierarchy,
or requires parser/tool choice, stop and request a design view from
`hdl-design-view-extractor` rather than inventing structure.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/timing/register-evidence.md`

## Configuration

The user may provide an optional config YAML to override defaults. If none is
provided, use `default_config.yaml`. The config controls:

- `depth_thresholds`: gate-level cutoffs for `critical`, `hard`, and `moderate`
- `gate_depth_model`: estimated gate levels per operation type
- `report`: path filtering, output caps, and sort order

Use the configured depth model for numeric estimates. If an operation does not
map cleanly to the model, decompose it into supported operations or emit the
assumption in the path text.

## Analysis

Perform these steps:

1. Identify sequential endpoints from explicit evidence in the design view or
   visible RTL. Record register name, width, clock, detection source, and line.
2. Build combinational fanin for each destination register until the trace hits
   another register, input port, constant, or unresolved object.
3. Include boundary paths when evidence is available:
   - input-to-register
   - register-to-output
   - input-to-output
4. Follow cross-module paths only when the design view or provided source proves
   the instance implementation and port bindings.
5. Estimate depth for each path by summing configured operation depths.
6. Categorize the path using `depth_thresholds`.
7. Suggest optimizations only for `critical` and `hard` paths, and state whether
   the suggestion likely changes latency.

## Output Format

Produce a single YAML document:

```yaml
module: <module_name>
file: <file_path_or_design_view_id>
config: <"default" or path to user config>

registers:
  - name: <register_name>
    width: <bits>
    clock: <clock_name>
    source: <"always_ff" | "macro" | "library_cell" | "inferred">
    line: <line_number>

paths:
  - id: PATH-<NNN>
    from: <source_register or "INPUT:port_name">
    to: <dest_register or "OUTPUT:port_name">
    depth: <estimated_gate_levels>
    difficulty: <"critical" | "hard" | "moderate" | "easy">
    stages:
      - op: <operation_type>
        width: <bit_width>
        depth: <gate_levels_contributed>
        line: <line_number>
    crosses_module: <true | false>
    module_path: ["top", "sub1"]
    description: <brief path summary>
    suggestion: <optimization hint, only for critical/hard>

unresolved:
  - name: <object_name>
    line: <line_number>
    reason: <"macro definition not found" | "unknown cell library" | "missing design view" | "missing submodule">

summary:
  total_registers: <N>
  total_paths: <N>
  by_difficulty:
    critical: <N>
    hard: <N>
    moderate: <N>
    easy: <N>
  deepest_path:
    id: <PATH-ID>
    depth: <N>
    from: <reg_or_input>
    to: <reg_or_output>
```

## Conventions

- Number path IDs sequentially: `PATH-001`, `PATH-002`, etc.
- Sort paths by depth descending, then by source order.
- Only list paths above `easy` unless config says `include_easy: true`.
- Keep descriptions to one sentence.
- Report unresolved hierarchy or unknown operations explicitly.

## Scope Limitations

- Can do: structural pre-synthesis path-depth estimation from a source-grounded
  design view or small visible RTL block.
- Cannot do: select or run extraction tools, elaborate unknown languages, perform
  gate-level netlist analysis, account for retiming or placement, infer timing
  exceptions, or replace PrimeTime, Tempus, Design Compiler, Fusion Compiler, or
  Genus timing analysis.

## Not Covered

- Clock tree analysis
- Hold time or min-delay paths
- False paths and multicycle paths without explicit constraints
- Power analysis
