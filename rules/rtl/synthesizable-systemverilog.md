# Synthesizable SystemVerilog

Use this rule whenever a skill emits or reviews RTL intended for synthesis.

## Required behavior

1. Emit synthesizable SystemVerilog only. Prefer `always_ff`, `always_comb`, and
   explicit reset behavior over ambiguous procedural style.
2. Keep one clear driver per register or output unless the interface semantics
   explicitly require otherwise.
3. Give combinational logic complete assignment coverage to avoid inferred
   latches unless a latch is an intentional design feature.
4. Keep clock, reset, and CDC structure explicit in the code and in review
   findings.
5. When the specification is incomplete, leave an unresolved item instead of
   choosing a hidden microarchitectural behavior.

## Prohibited behavior

- Do not emit non-synthesizable constructs such as `fork/join`, `program`,
  `class`, or simulation-only timing controls in synthesizable RTL modules.
- Do not silently choose a reset policy that is not grounded in the spec.
- Do not claim synthesis or signoff completeness from code style alone.
