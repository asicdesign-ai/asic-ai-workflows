---
name: design-intent-to-dv-objectives
description: >
  Convert a short block-level design-intent brief plus provided RTL context into a
  deterministic list of DV objectives. Use this skill whenever the user wants to
  turn design intent into verification targets, expected behaviors, or block-level
  success criteria before choosing tests, assertions, or coverage.
---

# Design Intent To DV Objectives Skill

Convert block-level design intent into stable DV objective records that downstream
skills can trace.

Scope: block or small IP. This is a planning skill, not a testbench generator.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/dv/objective-traceability.md`
- `../../rules/dv/stimulus-prioritization.md`

## Analysis

Read the design-intent brief and the provided RTL context, then perform these steps:

1. Extract explicit functional goals, reset behavior, configuration behavior, data
   movement behavior, status signaling, interrupt behavior, and error handling.
2. Merge duplicate intent statements into one objective when they describe the same
   verification target.
3. Assign a priority using `../../rules/dv/stimulus-prioritization.md`.
4. Mark each objective source as `design_intent`, `rtl`, or `both`.
5. Write one concrete success condition per objective.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: timer_counter
  rtl_files:
    - datasets/fixtures/dv/csr_timer_counter.sv
  intent_summary: "CSR-programmable timer with sticky interrupt behavior."

objectives:
  - id: OBJ-001
    title: reset establishes idle timer state
    priority: must
    source: both
    category: reset
    description: "Reset drives the timer count and interrupt outputs to their idle values."
    success_condition: "After reset, count_q is zero, irq is low, and the block is disabled until configured."

summary:
  total_objectives: 3
  by_priority:
    must: 2
    should: 1
    could: 0
```

## Scope Limitations

- **Can do**: derive deterministic DV objectives from explicit design intent and
  matching RTL structure.
- **Cannot do**: infer full system intent, firmware sequencing, or undocumented
  integration requirements.
