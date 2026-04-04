# DV Assertion Classification

Use this rule whenever a skill proposes SVA candidates for a DV plan.

## Assertion classes

- `reset`: reset values, reset exit behavior, and reset hold requirements
- `protocol`: handshakes, sequencing, and interface legality
- `state`: legal state transitions or state-dependent behavior
- `data_integrity`: counters, bounds, ordering, stable transfer conditions, or data
  preservation requirements
- `error`: explicit illegal command, overflow, underflow, or fault signaling

## Required behavior

1. Emit an assertion candidate only when the behavior is visible in RTL or stated
   in the design intent.
2. Classify each assertion candidate into exactly one class from this rule.
3. Prefer property candidates that can be checked from block-local signals.
4. If cycle timing, latency, or protocol stability is not explicit, keep the
   candidate conservative and note the uncertainty elsewhere.
5. Tie every assertion candidate back to one or more objective IDs.

## Prohibited behavior

- Do not invent cycle-accurate latency guarantees that are not present in the RTL
  or design intent.
- Do not propose formal assumptions as if they were proven block requirements.
- Do not emit an assertion candidate that depends on hidden hierarchy or absent
  interface semantics.
