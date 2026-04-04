# DV Objective Traceability

Use this rule whenever a DV artifact maps intent and RTL evidence into objectives,
tests, assertions, or coverage.

## Required behavior

1. Every downstream DV artifact must reference one or more objective IDs such as
   `OBJ-001`.
2. Every objective must state whether it came from `design_intent`, `rtl`, or
   `both`.
3. Do not create tests, assertions, coverage items, agents, scoreboards, or
   reference models that have no stated objective linkage.
4. If design intent and RTL disagree, record the conflict in an unresolved or risk
   section instead of silently choosing one interpretation.
5. If a plausible verification need cannot be tied to intent or explicit RTL
   structure, classify it as unresolved rather than fabricating an objective.

## Prohibited behavior

- Do not emit orphaned DV artifacts that are not traceable to an objective.
- Do not collapse multiple distinct objectives into one vague catch-all objective.
- Do not upgrade a speculative concern into a required objective without evidence.
