---
name: hdl-design-view-extractor
description: >
  Extract a source-grounded, AI-readable textual design view from HDL source,
  parser output, MCP tool output, or model reasoning. Use this skill when the
  user needs Verilog, SystemVerilog, VHDL, or proprietary hardware description
  language normalized into a reusable design view for downstream analysis flows
  such as timing, lint, CDC, RDC, formal planning, or DV planning. Prefer UHDM
  text for SystemVerilog/Verilog when available, AST JSON when UHDM is not
  available, and explicit model-derived views only when no tool evidence exists.
---

# HDL Design View Extractor Skill

Create a textual, source-grounded design view from HDL. The design view is an
intermediate representation for AI workflows: it should be readable by an LLM,
structured enough for deterministic validation, and explicit about evidence and
uncertainty.

This skill only extracts and normalizes design structure. It does not perform
timing, CDC, RDC, lint, synthesis, simulation, or functional verification.

## Rules

Apply these repo rules before extraction and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/common/tool-evidence-provenance.md`

## Source Preference

Use the strongest available source-backed view:

1. UHDM text dump for SystemVerilog or Verilog when available.
2. Parser AST/CST JSON, such as slang or pyslang JSON, when UHDM is unavailable.
3. MCP or tool-provided textual AST, elaborated design tree, or design graph for
   VHDL or proprietary languages.
4. Model-derived view from raw source text only when no tool-backed view exists.

Do not invent hierarchy, widths, clocks, resets, or sequential behavior. Use
`confidence: low` and `unresolved` when evidence is incomplete.

## Extraction

Perform these steps:

1. Identify the language and source artifact type.
2. Record tool provenance if an MCP, parser, or local command produced evidence.
3. Identify design units, ports, signals, instances, sequential elements, and
   combinational operations that are visible in the provided artifacts.
4. Preserve line evidence wherever possible.
5. Classify the design view format as `uhdm_text`, `ast_json`,
   `tool_design_graph`, or `model_derived`.
6. Emit unresolved entries for missing submodules, unknown cells, unknown
   language constructs, or inferred details that cannot be proven.

## Output Format

Produce a single YAML document:

```yaml
design:
  view_id: VIEW-001
  top_units:
    - simple_counter
  source_language: systemverilog
  source_files:
    - datasets/fixtures/hdl-design-view/simple_counter.sv

extraction:
  view_format: model_derived
  source_kind: rtl_source
  tool:
    name: none
    version: null
    evidence: "model-derived from visible source"
  confidence: high

ports:
  - name: clk
    direction: input
    width: 1
    role: clock
    line: 2

signals:
  - name: count_q
    width: 8
    kind: register
    line: 7

sequential_elements:
  - id: SEQ-001
    name: count_q
    kind: flip_flop
    width: 8
    clock: clk
    reset: rst_n
    evidence: "assigned in always_ff @(posedge clk or negedge rst_n)"
    line: 11
    confidence: high

combinational_nodes:
  - id: COMB-001
    op: adder
    output: count_d
    inputs:
      - count_q
      - "1"
    width: 8
    line: 16
    confidence: high

instances: []

unresolved: []

summary:
  total_design_units: 1
  total_ports: 4
  total_sequential_elements: 1
  total_combinational_nodes: 1
  total_instances: 0
  total_unresolved: 0
```

## Conventions

- Use `VIEW-001` unless the user asks for multiple views.
- Number sequential elements as `SEQ-001`, `SEQ-002`, etc.
- Number combinational nodes as `COMB-001`, `COMB-002`, etc.
- Preserve source names exactly.
- Use `unknown` for language when the source language cannot be established.
- Use `model_derived` only when no UHDM, AST JSON, or tool design graph is
  available.

## Scope Limitations

- Can do: produce a compact design view suitable for downstream AI skills and
  flows.
- Cannot do: prove timing closure, run synthesis, simulate behavior, validate
  CDC/RDC safety, or guarantee full language elaboration without tool evidence.
