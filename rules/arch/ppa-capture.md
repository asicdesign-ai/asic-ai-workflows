# PPA Capture

Use this rule whenever a skill collects or normalizes power, performance, and
area constraints.

## Required behavior

1. Capture `performance`, `power`, and `area` explicitly as separate targets.
2. Preserve whether each target is numeric, qualitative, or missing.
3. Keep user-provided units verbatim when they are explicit, such as `MHz`,
   `mW`, `um^2`, or utilization budgets.
4. If a target is missing, emit an open question or unresolved item rather than
   filling in a default value.
5. If the user supplies priorities instead of numbers, record those priorities as
   qualitative targets and keep the missing numeric target visible.

## Prohibited behavior

- Do not invent numeric PPA values.
- Do not collapse `power`, `performance`, and `area` into one combined priority.
- Do not treat a qualitative preference as proof of closure.
