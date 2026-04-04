# DV Coverage Taxonomy

Use this rule whenever a skill plans functional coverage for a block-level DV flow.

## Required behavior

1. Cover reset behavior, nominal behavior, and corner behavior whenever those
   behaviors exist in the provided inputs.
2. Cover configuration space when the block exposes configuration controls or modes.
3. Cover error behavior when the block exposes explicit error outputs, illegal
   commands, overflow, underflow, or similar fault paths.
4. Use crosses only when they verify a meaningful interaction, such as mode by
   error, command by state, or configuration by output behavior.
5. Add exclusions only when the reason is explicit and the excluded case stays tied
   to the affected objectives.
6. Tie every coverpoint, cross, and exclusion back to one or more objective IDs.

## Prohibited behavior

- Do not add decorative coverage that has no verification purpose.
- Do not create exhaustive configuration crosses when the interaction is not
  meaningful to the objectives.
- Do not omit error or corner coverage when the RTL visibly implements those paths.
