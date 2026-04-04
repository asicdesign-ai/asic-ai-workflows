---
name: functional-coverage-planner
description: >
  Build a block-level functional coverage plan from objectives and RTL surface
  information. Use this skill whenever the user wants deterministic coverpoints,
  crosses, and exclusions tied back to explicit verification objectives.
---

# Functional Coverage Planner Skill

Plan block-level functional coverage tied to explicit DV objectives.

Scope: block or small IP. This is a planning skill, not coverage code generation.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/dv/objective-traceability.md`
- `../../rules/dv/coverage-taxonomy.md`

## Analysis

Read the DV objectives and RTL verification surface, then perform these steps:

1. Identify reset, configuration, nominal, error, and corner behaviors that need
   functional coverage.
2. Add coverpoints for direct observables and meaningful internal state when visible.
3. Add crosses only when they verify a meaningful interaction required by the
   objectives.
4. Add exclusions only when the reason is explicit from the RTL or design intent.
5. Trace every coverage item back to one or more objective IDs.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: missing_intent_block

coverpoints:
  - id: COV-001
    objective_ids:
      - OBJ-001
    target: enable
    kind: configuration
    description: "Cover enable transitions seen at the block input."

crosses:
  - id: COV-002
    objective_ids:
      - OBJ-002
    targets:
      - enable
      - busy
    description: "Cross enable programming with observed busy behavior."

exclusions:
  - id: COV-003
    objective_ids:
      - OBJ-002
    related_targets:
      - enable
      - busy
    rationale: "Do not require latency-specific bins because the design intent does not define response timing."

summary:
  total_coverpoints: 2
  total_crosses: 1
  total_exclusions: 1
```

## Scope Limitations

- **Can do**: produce deterministic coverage intent tied to explicit objectives.
- **Cannot do**: derive exhaustive system coverage, coverage closure strategy, or
  undocumented latency bins.
