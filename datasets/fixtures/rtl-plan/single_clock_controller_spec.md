# Single Clock Controller Microarchitecture

## Overview

`single_clock_controller` counts qualified `tick_i` events after `start_i` and
asserts `done_o` for one cycle when the programmed terminal count is reached.

## Interfaces

- `clk_i`
- `rst_n`
- `start_i`
- `stop_i`
- `tick_i`
- `threshold_i[7:0]`
- `busy_o`
- `done_o`

## State

- `busy_q`
- `count_q[7:0]`

## Behavior

- reset clears `busy_q`, `count_q`, and `done_o`
- `start_i` arms counting and clears the count
- `tick_i` increments `count_q` while busy
- `stop_i` clears `busy_q`
- threshold match drives a one-cycle `done_o` pulse and clears `busy_q`
