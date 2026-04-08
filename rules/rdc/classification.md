# RDC Classification

Use this rule whenever a skill analyzes reset domain crossing (RDC) behavior.

## Required behavior

1. Treat two signals as different reset domains when their controlling resets
   differ in name, polarity, or assertion style and the relationship is not
   explicitly proven safe.
2. Flag a crossing when logic released by one reset is sampled by logic released
   by a different reset domain.
3. Classify a crossing as `protected` only when the provided RTL shows an
   explicit stabilizing structure such as synchronized release, reset bridge
   logic, or clear staging in the destination domain.
4. Use `critical`, `high`, `medium`, `low`, and `info` severities consistently:
   unsafely sampled control state should be `critical` or `high`; informational
   protected structures may be `info`.
5. Emit the smallest valid remediation for medium-or-higher findings.

## Prohibited behavior

- Do not treat identical signal names as proof of identical reset behavior unless
  the wiring is visible in the provided RTL.
- Do not mark a naming convention such as `_sync_rst` as proof of protection.
- Do not conflate RDC with CDC; keep reset-domain hazards separate from clock
  crossings.
