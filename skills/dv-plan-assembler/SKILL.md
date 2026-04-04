---
name: dv-plan-assembler
description: >
  Assemble a block-level DV plan from objectives, RTL surface data, UVM test
  planning, SVA candidates, functional coverage, and optional CDC or timing risk
  reports. Use this skill whenever the user wants one final structured DV plan
  with deterministic IDs, explicit unresolved items, and a UVM-centric environment
  recommendation.
---

# DV Plan Assembler Skill

Merge block-level DV planning artifacts into one final plan.

Scope: block or small IP. This is a planning skill, not testbench generation.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/dv/objective-traceability.md`
- `../../rules/dv/uvm-component-selection.md`
- `../../rules/dv/assertion-classification.md`
- `../../rules/dv/coverage-taxonomy.md`
- `../../rules/dv/stimulus-prioritization.md`

## Analysis

Read the intermediate DV artifacts and optional CDC or timing reports, then perform
these steps:

1. Merge objectives, interfaces, environment, tests, assertions, and coverage into
   one deterministic plan.
2. Deduplicate overlapping descriptions while preserving objective linkage.
3. Import CDC and timing findings only as risk and prioritization inputs.
4. Emit unresolved items for missing protocol, latency, or intent detail rather
   than inventing plan content.
5. Keep IDs stable by preserving the intermediate namespaces `OBJ`, `TEST`, `SVA`,
   `COV`, and `RISK`.

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

interfaces:
  - name: cfg_enable
    direction: input
    role: config
    width: 1

env:
  agents: []
  monitors: []
  scoreboards: []
  reference_models: []
  virtual_sequences: []

tests:
  - id: TEST-001
    title: timer reset behavior
    objective_ids:
      - OBJ-001
    stimulus: directed
    checkers:
      - irq_reset_check
    priority: must
    description: "Apply reset and verify count and interrupt outputs return to idle."

assertions:
  - id: SVA-001
    title: irq clears on reset
    objective_ids:
      - OBJ-001
    class: reset
    source: rtl
    bind_target: timer_counter
    description: "Reset clears the interrupt output."

coverage:
  coverpoints: []
  crosses: []
  exclusions: []

risks:
  - id: RISK-001
    source: timing_report
    severity: medium
    objective_ids:
      - OBJ-002
    description: "A hard timer compare path should receive early stress and assertion attention."

unresolved:
  - id: UNR-001
    item: irq pulse width
    reason: "The design intent does not define whether irq must pulse or remain sticky until clear."
    objective_ids:
      - OBJ-003

summary:
  total_objectives: 3
  total_tests: 3
  total_assertions: 2
  total_coverage_items: 3
  total_risks: 1
  total_unresolved: 1
```

## Scope Limitations

- **Can do**: assemble a deterministic block-level DV plan and import optional risk
  signals from other reports.
- **Cannot do**: generate executable UVM code, resolve contradictory intent without
  evidence, or claim signoff completeness.
