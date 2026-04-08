---
name: block-requirements-normalizer
description: >
  Normalize a block-level design brief into deterministic requirements, explicit
  PPA targets, and open intake questions. Use this skill whenever the user
  provides high-level microarchitectural intent and the workflow must capture
  power, performance, and area before specification or RTL work begins.
---

# Block Requirements Normalizer Skill

Convert a user brief into one structured requirement set for a block-level RTL
planning flow.

Scope: block or small IP. This is an intake and normalization skill, not a
microarchitecture or RTL generator.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/arch/requirements-traceability.md`
- `../../rules/arch/ppa-capture.md`

## Analysis

Read the user brief and any optional RTL context, then perform these steps:

1. Extract atomic block requirements and assign stable `REQ-NNN` IDs.
2. Separate functional, interface, clock/reset, and PPA requirements.
3. Capture `performance`, `power`, and `area` independently as numeric,
   qualitative, or missing.
4. Emit blocking open questions whenever the intake does not support
   specification work, especially for missing PPA.
5. Keep descriptions short, factual, and grounded in the provided brief.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: event_counter
  brief_summary: "Programmable event counter with optional interrupt threshold."

requirements:
  - id: REQ-001
    title: count qualified input events
    category: function
    priority: must
    source: user
    description: "The block increments a stored count when event_valid is asserted."
    acceptance_criteria: "With counting enabled, each qualified event increments count_value by one."

ppa_targets:
  performance:
    target: "600"
    units: "MHz"
    priority: "primary"
    status: numeric
  power:
    target: "minimize dynamic power"
    units: null
    priority: "secondary"
    status: qualitative
  area:
    target: null
    units: null
    priority: "secondary"
    status: missing

open_questions:
  - topic: area target
    question: "What area budget or utilization limit constrains the block?"
    blocking: true
    related_requirement_ids:
      - REQ-001

summary:
  total_requirements: 1
  total_open_questions: 1
  ppa_complete: false
```

## Scope Limitations

- **Can do**: normalize intent, capture explicit PPA status, and surface missing
  intake data.
- **Cannot do**: derive a complete microarchitecture, choose undocumented
  protocols, or claim front-end closure.
