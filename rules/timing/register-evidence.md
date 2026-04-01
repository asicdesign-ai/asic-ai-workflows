# Timing Register Evidence

Use this rule when identifying sequential elements and building pre-synthesis timing
paths from RTL.

## Accepted evidence for registers

Treat an object as a register only when at least one of these is visible in the
provided RTL:

- an `always_ff` block or an edge-triggered `always @(posedge/negedge ...)` block
- an in-scope macro definition that clearly instantiates sequential logic
- a library cell or wrapper whose ports and naming clearly expose sequential behavior
- a module instance whose implementation is provided and proves sequential behavior

FF-like names such as `DFF_X1`, `u_reg`, or `state_ff` are useful hints, but they are
not sufficient proof by themselves when ports or definitions are missing.

## Unresolved handling

1. If a macro, cell, or wrapper cannot be proven sequential or combinational from the
   provided inputs, emit it in `unresolved`.
2. Do not silently trace through unresolved objects.
3. Do not invent cross-module logic when the submodule source is absent.
4. If an operation does not map cleanly to the configured depth model, either decompose
   it into supported operations or report the assumption explicitly in the path text.

## Required behavior

- Use the configured depth model for numeric estimates; do not substitute ad hoc
  formulas.
- Prefer conservative path construction over optimistic guessing when structure is
  incomplete.

## Prohibited behavior

- Do not claim a path is safe because "synthesis will optimize it away" unless the
  skill config explicitly models that structure.
- Do not infer false paths, multicycle paths, generated clocks, or other timing
  exceptions without user-provided constraints.
- Do not trace through unresolved macros, cells, wrappers, or missing submodule logic
  as though their timing behavior were known.
