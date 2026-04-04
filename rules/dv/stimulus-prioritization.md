# DV Stimulus Prioritization

Use this rule whenever a DV skill assigns objective or test priority.

## Priority levels

- `must`: reset, safety, error handling, externally visible correctness, or core
  data/control behavior that defines block functionality
- `should`: meaningful secondary behavior, integration-oriented scenarios, or
  stress cases that are important but not foundational
- `could`: exploratory or optional scenarios that add confidence without being
  essential for first-pass block signoff

## Required behavior

1. Assign `must` to behavior required for basic block correctness or safety.
2. Assign `should` to important but non-foundational scenarios such as secondary
   modes, longer stress, or observability improvements.
3. Assign `could` only to optional scenarios that remain useful after all `must`
   and `should` needs are satisfied.
4. Keep priority consistent between objectives and derived tests where the same
   verification intent is preserved.

## Prohibited behavior

- Do not label a scenario `must` without a clear correctness or safety rationale.
- Do not demote explicit error handling or reset behavior below `should`.
- Do not use priority labels as vague emphasis without concrete meaning.
