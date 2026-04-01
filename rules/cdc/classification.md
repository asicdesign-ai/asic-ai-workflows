# CDC Classification

Use this rule when classifying clock domain crossings in RTL.

## Synchronizer evidence requirements

Treat a crossing as synchronized only when the protection structure is explicit in the
provided RTL. Naming alone is not sufficient.

- `2ff` or `3ff`: require an explicit chain of two or three destination-domain
  registers carrying the same single-bit signal in sequence.
- `gray`: require a Gray-coded source value plus destination-domain synchronizer
  stages on that value before use.
- `handshake`: require a synchronized request path, a synchronized acknowledge path,
  and evidence that the multi-bit data remains stable across the transfer window.
- `toggle_snapshot`: require an explicit source-side toggle, destination-side toggle
  synchronization, and edge-based capture of stable data.
- `pulse_sync`: require pulse-to-toggle conversion or an equivalent explicit pulse
  transfer structure in the RTL. A plain 2-FF chain on a narrow pulse is not enough.
- `async_fifo`: require dual-clock storage semantics plus synchronized Gray-style or
  equivalent protected pointer transfer across domains.

If the RTL does not prove one of these structures, classify the crossing as not
proven synchronized.

## Severity mapping

- `critical`: multi-bit crossing without proven safe transport
- `high`: single-bit crossing without proven synchronization
- `medium`: partially protected or structurally flawed crossing, such as a pulse that
  can be missed or a multi-bit transfer with incomplete protocol evidence
- `low`: ambiguous or quasi-static case where the RTL is insufficient to confirm safety
- `info`: protection is explicitly present and structurally consistent

## Required behavior

1. Prove synchronization from structure, not intent.
2. When a pattern is only partially visible, classify conservatively as `medium` or
   `low` instead of `info`.
3. For multi-bit crossings, do not bless a plain bitwise 2-FF scheme as safe data
   transfer unless the structure is explicitly Gray-coded and used accordingly.

## Prohibited behavior

- Do not claim a crossing is synchronized unless the synchronizer structure is visible.
- Do not classify a CDC path as `info` from naming conventions alone, including
  names like `_sync`, `gray`, `req`, or `ack`.
- Do not treat a plain bitwise 2-FF scheme on a multi-bit bus as safe transfer unless
  the RTL explicitly proves a valid protocol such as Gray-code, handshake, toggle
  snapshot, or async FIFO semantics.
