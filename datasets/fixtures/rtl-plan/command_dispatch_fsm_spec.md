# Command Dispatch FSM Microarchitecture

## Overview

`command_dispatch_fsm` sequences command acceptance, execution, and fault
recovery with a four-state controller.

## States

- `IDLE`
- `LOAD`
- `EXEC`
- `ERROR`

## Behavior

- `cmd_valid_i` takes the block from `IDLE` to `LOAD`
- `LOAD` transitions to `EXEC` after one cycle
- `fault_i` forces `ERROR`
- `clear_i` returns `ERROR` to `IDLE`
