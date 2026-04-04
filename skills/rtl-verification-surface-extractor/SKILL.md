---
name: rtl-verification-surface-extractor
description: >
  Extract the block-level verification surface from provided Verilog or
  SystemVerilog RTL. Use this skill whenever the user wants a structured summary
  of clocks, resets, interfaces, state-visible behaviors, observability points,
  and unresolved verification gaps before building a DV plan.
---

# RTL Verification Surface Extractor Skill

Extract the externally visible and verification-relevant RTL surface for a block or
small IP.

Scope: block or small IP. This is a structural planning skill, not a lint tool.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`

## Analysis

Read the provided RTL and perform these steps:

1. Identify clocks and resets from sequential blocks and reset conditions.
2. Extract module ports and classify each interface by verification role.
3. Identify verification-relevant state elements such as counters, flags, control
   registers, FSM state, and buffers.
4. Summarize visible behaviors that matter for verification, including reset,
   transactions, status updates, interrupts, error paths, and backpressure.
5. Record observability points and unresolved gaps where the RTL is insufficient to
   determine intent or timing semantics.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: streaming_buffer
  rtl_files:
    - datasets/fixtures/dv/streaming_buffer.sv

clocks:
  - name: clk
    line: 12

resets:
  - name: rst_n
    active: active_low
    style: async
    line: 12

interfaces:
  - name: in_valid
    direction: input
    role: handshake
    width: 1
    line: 6

state_elements:
  - name: full_q
    kind: flag
    clock: clk
    line: 21

behaviors:
  - id: BEH-001
    kind: backpressure
    description: "The block deasserts in_ready when the single-entry buffer is full."
    evidence:
      - file: datasets/fixtures/dv/streaming_buffer.sv
        line: 18
        signal: in_ready

observability:
  - signal: out_valid
    role: status
    line: 19

unresolved:
  - name: pass-through latency
    reason: "The RTL does not state whether zero-cycle forwarding is a verification requirement."
    line: 18

summary:
  total_interfaces: 9
  total_state_elements: 2
  total_behaviors: 3
  total_unresolved: 1
```

## Scope Limitations

- **Can do**: identify verification-relevant interfaces, state, and visible block
  behavior from provided RTL.
- **Cannot do**: infer undocumented protocol timing, system traffic assumptions, or
  hidden hierarchy behavior.
