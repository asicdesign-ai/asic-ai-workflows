# Dual Clock Event Bridge Brief

Create a small block that accepts a pulse in `src_clk_i` and exposes a single
cycle event indication in `dst_clk_i`.

Requirements:

- source and destination clocks are asynchronous
- destination must not lose back-to-back pulses beyond the documented limit
- destination logic must expose `dst_event_o`
- the design should stay small and timing-friendly

PPA:

- performance: 400 MHz target in destination clock domain
- power: low
- area: small bridge logic
