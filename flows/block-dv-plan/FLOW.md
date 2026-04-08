---
name: block-dv-plan
description: >
  Build a block-level, UVM-centric DV plan from RTL files and a short design-intent
  brief. Use this flow whenever the user wants a DV expert workflow for a block or
  small IP that ends in a structured verification plan rather than runnable code.
---

# Block DV Plan Flow

Build one final DV plan for a block or small IP from design intent, RTL evidence,
and optional CDC or timing risk reports.

## Inputs

- `top_module`
- `rtl_files[]`
- `design_intent`
- optional `block_rtl_package`
- optional `cdc_report`
- optional `timing_report`

## Trigger Phrases

Use this flow when the user asks for block-level DV planning with phrases such as:

- `DV plan`
- `verification plan`
- `block-level DV`
- `IP verification plan`
- `UVM plan`
- `UVM test plan`
- `verification strategy`
- `derive DV objectives`
- `analyze RTL for verification`
- `what should we verify`
- `create assertions and coverage plan`
- `act as a DV expert`

Example requests:

- "Create a block-level DV plan for this RTL."
- "Build a UVM-centric verification plan from this IP and design intent."
- "Analyze this block and propose tests, assertions, and functional coverage."
- "Act as a DV expert and plan verification for this module."

## Rules

Apply these repo rules across the flow:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/dv/objective-traceability.md`
- `../../rules/dv/uvm-component-selection.md`
- `../../rules/dv/assertion-classification.md`
- `../../rules/dv/coverage-taxonomy.md`
- `../../rules/dv/stimulus-prioritization.md`

## Skills

Run these skills in order:

1. `../../skills/design-intent-to-dv-objectives/SKILL.md`
2. `../../skills/rtl-verification-surface-extractor/SKILL.md`
3. `../../skills/uvm-test-matrix-planner/SKILL.md`
4. `../../skills/sva-candidate-planner/SKILL.md`
5. `../../skills/functional-coverage-planner/SKILL.md`
6. `../../skills/dv-plan-assembler/SKILL.md`

## Execution

1. Derive deterministic DV objectives from design intent and visible RTL behavior.
2. Extract the verification surface from the same RTL set.
3. Plan the minimal greenfield UVM environment and prioritized tests.
4. Plan assertion candidates grounded in visible block behavior.
5. Plan functional coverage tied to the same objectives.
6. When `block_rtl_package` is provided from `block-level-rtl-plan`, use its
   requirement traceability, microarchitecture spec path, and audit summary as
   additional planning context while keeping the final DV plan grounded in the
   provided spec and RTL.
7. Assemble the final plan and import optional CDC or timing reports only as risks.
8. Emit unresolved items when intent, latency, or protocol detail is missing.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: timer_counter
  rtl_files:
    - datasets/fixtures/dv/csr_timer_counter.sv
  intent_summary: "CSR-programmable timer with sticky interrupt behavior."

objectives: []
interfaces: []

env:
  agents: []
  monitors: []
  scoreboards: []
  reference_models: []
  virtual_sequences: []

tests: []
assertions: []

coverage:
  coverpoints: []
  crosses: []
  exclusions: []

risks: []
unresolved: []

summary:
  total_objectives: 0
  total_tests: 0
  total_assertions: 0
  total_coverage_items: 0
  total_risks: 0
  total_unresolved: 0
```

## Scope Limitations

- **Can do**: create a block-level, UVM-centric verification plan with objective
  traceability and optional risk import.
- **Cannot do**: generate runnable UVM code, debug regressions, or plan SoC-level
  verification architecture.
