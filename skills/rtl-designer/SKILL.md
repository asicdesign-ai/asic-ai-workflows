---
name: rtl-designer
description: >
  Read an approved microarchitecture specification and emit synthesizable
  SystemVerilog with requirement traceability. Use this skill whenever the flow
  moves from block architecture into concrete RTL implementation.
---

# RTL Designer Skill

Generate synthesizable SystemVerilog from a block-level microarchitecture
specification.

Scope: block or small IP. This skill emits RTL artifacts, not synthesis scripts
or signoff collateral.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/common/tool-evidence-provenance.md`
- `../../rules/arch/requirements-traceability.md`
- `../../rules/rtl/synthesizable-systemverilog.md`

## Analysis

Read the approved microarchitecture specification and perform these steps:

1. If project context is provided and HDL/EDA MCP tools are available, collect
   read-only evidence before generation using the optional MCP-assisted context
   rules below.
2. Partition the design into the minimal synthesizable SystemVerilog modules
   required by the spec.
3. Keep clocks, resets, interface semantics, and state updates explicit.
4. Preserve traceability from each requirement into emitted RTL files and
   signals.
5. Emit unresolved items when the spec still leaves an implementation decision
   open.
6. Keep generated code block-level and front-end scoped.
7. If generated `source_files` are materialized to disk by an execution harness,
   optional read-only MCP diagnostics may be used as post-generation evidence.

## Optional MCP-Assisted Context

When MCP tools are available, use them only as evidence sources. Discover tools
by declared capability and schema, not by vendor name. Prefer read-only HDL/EDA
tools that can parse a project or filelist, report diagnostics, list design
units, describe modules/interfaces/packages, inspect hierarchy, or find symbols.

Use optional MCP context when the user provides a `project_root`, filelist,
existing RTL files, package/interface files, or generated RTL already
materialized on disk. Do not require MCP evidence for normal spec-to-RTL
generation.

`pyslang-mcp` is the baseline open semantic MCP for this skill. Useful calls
include `pyslang_parse_filelist` or `pyslang_parse_files`,
`pyslang_get_project_summary`, `pyslang_list_design_units`,
`pyslang_describe_design_unit`, `pyslang_get_hierarchy`, and
`pyslang_find_symbol`. After generated source files are materialized,
`pyslang_get_diagnostics` can provide compiler-backed parse or semantic
feedback. A clean `pyslang-mcp` diagnostic result is not synthesis, simulation,
lint, CDC, timing, or signoff evidence.

For vendor or internal EDA MCPs, use the same pattern only when the exposed tool
schema clearly provides read-only parse, elaboration, context, hierarchy, symbol,
or diagnostic queries. Do not assume Cadence, Synopsys, Siemens, Mentor, or other
vendor tool names or capabilities.

Do not call destructive or implementation-changing EDA tools from this skill. If
a tool can synthesize, simulate, edit RTL, run CDC, run timing, or launch signoff
flows, use it only when a downstream flow explicitly asks for that phase.

If MCP evidence is unavailable, incomplete, or degraded, continue from the
microarchitecture spec and record the limitation as `unresolved` when it affects
the generated RTL. Emit `tool_evidence: []` when no MCP evidence was used.
When tool evidence is present, each entry must contain `source`, `tools`,
`purpose`, `status`, and `summary`.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: event_counter
  brief_summary: "Programmable event counter with optional interrupt threshold."

source_files:
  - path: rtl/event_counter.sv
    module: event_counter
    language: systemverilog
    content: |
      module event_counter (
          input  logic clk,
          input  logic rst_n,
          input  logic event_valid,
          output logic [7:0] count_value
      );
        always_ff @(posedge clk or negedge rst_n) begin
          if (!rst_n) begin
            count_value <= '0;
          end else if (event_valid) begin
            count_value <= count_value + 8'd1;
          end
        end
      endmodule

rtl_modules:
  - name: event_counter
    role: top
    clocks:
      - clk
    resets:
      - rst_n
    description: "Counts qualified events and exposes the stored count."

traceability:
  - requirement_id: REQ-001
    spec_sections:
      - overview
      - datapath
    rtl_files:
      - rtl/event_counter.sv
    rtl_signals:
      - event_valid
      - count_value

unresolved: []

tool_evidence: []

summary:
  total_source_files: 1
  total_modules: 1
  total_trace_links: 1
  total_unresolved: 0
```

## Scope Limitations

- **Can do**: emit synthesizable block-level SystemVerilog with requirement
  traceability and optional read-only tool evidence provenance.
- **Cannot do**: claim lint cleanliness, CDC safety, or signoff completeness
  without downstream audit skills.
