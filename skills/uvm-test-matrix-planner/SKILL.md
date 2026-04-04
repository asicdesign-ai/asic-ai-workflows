---
name: uvm-test-matrix-planner
description: >
  Build a block-level, UVM-centric DV test matrix from objectives and RTL surface
  information. Use this skill whenever the user wants a greenfield UVM environment
  recommendation, prioritized test scenarios, and justified monitors, scoreboards,
  reference models, or virtual sequences.
---

# UVM Test Matrix Planner Skill

Plan a block-level UVM environment and prioritized test matrix.

Scope: block or small IP. This is a planning skill, not UVM code generation.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/dv/objective-traceability.md`
- `../../rules/dv/uvm-component-selection.md`
- `../../rules/dv/stimulus-prioritization.md`

## Analysis

Read the DV objectives and RTL verification surface, then perform these steps:

1. Choose the minimal UVM environment that can verify the stated objectives.
2. Classify agents as `active` or `passive` using
   `../../rules/dv/uvm-component-selection.md`.
3. Add monitors, scoreboards, reference models, and virtual sequences only when
   justified by visible behavior and checking needs.
4. Build a prioritized test list that traces every test back to one or more
   objective IDs.
5. Keep the environment greenfield and block-local unless the inputs explicitly
   require more.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: status_fifo

env:
  bench_style: greenfield_uvm
  agents:
    - name: write_agent
      interface: write_side
      mode: active
      justification: "The bench must drive writes to exercise fill, overflow, and status behavior."
  monitors:
    - name: read_monitor
      interface: read_side
      justification: "Read-side activity must be observed for ordering and underflow checks."
  scoreboards:
    - name: fifo_order_scoreboard
      compares: "Expected FIFO order against read data and level updates."
      justification: "Data ordering cannot be checked by signal legality alone."
  reference_models:
    - name: fifo_reference_model
      scope: "Golden queue model for occupancy and data order."
  virtual_sequences:
    - name: reset_fill_drain_vseq
      objective_ids:
        - OBJ-001
        - OBJ-002
      description: "Coordinates reset, burst writes, and burst reads."

tests:
  - id: TEST-001
    title: fifo reset and empty behavior
    objective_ids:
      - OBJ-001
    stimulus: directed
    checkers:
      - fifo_order_scoreboard
    priority: must
    description: "Reset the FIFO and verify empty status, read gating, and clean level initialization."

summary:
  total_tests: 3
  by_priority:
    must: 2
    should: 1
    could: 0
```

## Scope Limitations

- **Can do**: recommend a block-level UVM environment and test list tied to explicit
  objectives.
- **Cannot do**: generate full class code, integration-level agent reuse policy, or
  regression triage.
