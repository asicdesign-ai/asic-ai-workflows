# Command FSM Intent

- Command `01` starts work from idle.
- Command `10` completes work when the block is busy.
- Command `11` aborts the busy state and returns to idle.
- Unsupported commands raise `error_flag`.
- Reset returns the block to idle with no pending completion pulse.
