# Timer Counter Intent

- The block is a CSR-controlled timer.
- `cfg_enable` enables free-running increment behavior.
- `cfg_load` loads `cfg_data` into the timer count.
- `irq` asserts when the count reaches `terminal_count`.
- `irq` remains asserted until software drives `clear_irq`.
- Reset returns the block to an idle disabled state with count zero.
