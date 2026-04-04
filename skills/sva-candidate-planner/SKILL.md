---
name: sva-candidate-planner
description: >
  Plan assertion candidates for a block-level DV effort from objectives and RTL
  evidence. Use this skill whenever the user wants reset, protocol, state,
  data-integrity, or error property candidates that are grounded in visible
  behavior rather than speculative timing assumptions.
---

# SVA Candidate Planner Skill

Plan block-level assertion candidates that a DV or formal engineer could implement.

Scope: block or small IP. This is a planning skill, not automatic SVA generation.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/dv/objective-traceability.md`
- `../../rules/dv/assertion-classification.md`

## Analysis

Read the DV objectives and RTL verification surface, then perform these steps:

1. Identify verification behaviors that can be monitored with block-local
   properties.
2. Classify each candidate using `../../rules/dv/assertion-classification.md`.
3. Prefer candidates with explicit signals, states, or interfaces in the RTL.
4. Avoid inventing cycle-accurate latency or system-level assumptions.
5. Trace every candidate back to one or more objective IDs.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: command_fsm

assertions:
  - id: SVA-001
    title: illegal command raises error
    objective_ids:
      - OBJ-003
    class: error
    source: both
    bind_target: command_fsm
    description: "When cmd_valid carries an unsupported opcode, error_flag asserts on the next state update."

summary:
  total_assertions: 3
  by_class:
    reset: 1
    protocol: 1
    state: 0
    data_integrity: 0
    error: 1
```

## Scope Limitations

- **Can do**: propose grounded property candidates for block-local behavior.
- **Cannot do**: prove properties, derive full formal assumption sets, or invent
  undocumented timing guarantees.
