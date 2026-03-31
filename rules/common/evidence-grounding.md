# Evidence Grounding

Use this rule whenever a skill analyzes RTL and emits findings.

## Required behavior

1. Ground every reported fact in the provided source. Each finding must be traceable
   to explicit RTL evidence such as signal names, clocks, operations, hierarchy, and
   line numbers that appear in the input.
2. Do not invent missing structure. If a macro definition, library cell behavior,
   submodule implementation, generated clock relationship, or timing exception is not
   present in the provided inputs, do not assume it exists.
3. Treat naming as a hint, not proof. Names like `_sync`, `gray_ptr`, `dff`, or
   `fast_clk` can guide inspection but cannot by themselves prove safety, function,
   or timing intent.
4. When evidence is incomplete, emit the most conservative supported result and say
   why briefly. Use the skill's uncertainty bucket such as `low` or `unresolved`
   rather than silently guessing.
5. Only claim widths, clock domains, module paths, or operation types that can be
   derived from the given RTL text. If exact width or structure cannot be confirmed,
   state the uncertainty in the finding instead of fabricating detail.

## Prohibited behavior

- Do not claim a crossing is synchronized unless the synchronizer structure is visible.
- Do not claim a path is safe because "synthesis will optimize it away" unless the
  skill config explicitly models that structure.
- Do not infer false paths, multicycle paths, or generated clocks without user-provided
  constraints.
