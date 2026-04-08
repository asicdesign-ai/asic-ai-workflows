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
- `../../rules/arch/requirements-traceability.md`
- `../../rules/rtl/synthesizable-systemverilog.md`

## Analysis

Read the approved microarchitecture specification and perform these steps:

1. Partition the design into the minimal synthesizable SystemVerilog modules
   required by the spec.
2. Keep clocks, resets, interface semantics, and state updates explicit.
3. Preserve traceability from each requirement into emitted RTL files and
   signals.
4. Emit unresolved items when the spec still leaves an implementation decision
   open.
5. Keep generated code block-level and front-end scoped.

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

summary:
  total_source_files: 1
  total_modules: 1
  total_trace_links: 1
  total_unresolved: 0
```

## Scope Limitations

- **Can do**: emit synthesizable block-level SystemVerilog with requirement
  traceability.
- **Cannot do**: claim lint cleanliness, CDC safety, or signoff completeness
  without downstream audit skills.
