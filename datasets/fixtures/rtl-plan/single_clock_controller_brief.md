# Single Clock Controller Brief

Design a block-level controller that accepts `start_i`, `stop_i`, and `tick_i`
inputs and raises `done_o` after a programmable number of ticks.

Requirements:

- single synchronous clock domain
- active-low asynchronous reset
- one-cycle `done_o` pulse when the terminal count is reached
- software-visible `busy_o` status

PPA:

- performance: 500 MHz target
- power: low dynamic power is secondary to timing
- area: keep the controller compact
