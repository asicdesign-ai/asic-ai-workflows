# UVM Component Selection

Use this rule whenever a skill proposes a UVM environment or test structure.

## Required behavior

1. Add an agent only when the block exposes a meaningful transaction or pin-level
   interface that the bench must drive or monitor.
2. Mark an agent `active` only when the plan requires the testbench to drive that
   interface. Otherwise prefer a passive monitor.
3. Add a scoreboard only when observed behavior must be compared against expected
   data, ordering, or state evolution.
4. Add a reference model only when the scoreboard needs a predictive model beyond
   direct signal checking.
5. Add virtual sequences only when the plan must coordinate reset, configuration,
   and one or more active traffic phases across multiple components.
6. Prefer the smallest environment that can verify the stated objectives.

## Prohibited behavior

- Do not add a scoreboard, reference model, or virtual sequence "just in case".
- Do not propose bus agents, register models, or predictors that are not justified
  by the provided RTL interfaces or design intent.
- Do not mark an interface active when the plan only needs observation.
