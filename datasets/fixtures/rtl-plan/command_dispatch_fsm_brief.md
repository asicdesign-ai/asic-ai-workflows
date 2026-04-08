# Command Dispatch FSM Brief

Create a command dispatcher with `IDLE`, `LOAD`, `EXEC`, and `ERROR` states.

Requirements:

- start in `IDLE`
- move to `LOAD` on `cmd_valid_i`
- move to `EXEC` after one load cycle
- move to `ERROR` on `fault_i`
- return to `IDLE` on `clear_i`

PPA:

- performance: 650 MHz target
- power: balanced
- area: compact control logic
