# RTL Understanding V1 Seed Corpus

This directory seeds the first structured corpus work for publishable RTL
datasets.

Current scope:

- ten canary records across two deterministic tasks
- five existing repo fixtures as canonical RTL sources
- one provenance file per record
- explicit `train`, `validation`, and `test` split files

Current source modules:

- `datasets/fixtures/rtl-plan/single_clock_controller.sv`
- `datasets/fixtures/rtl-plan/dual_clock_event_bridge.sv`
- `datasets/fixtures/rtl-plan/load_store_command_processor.sv`
- `datasets/fixtures/rtl-plan/warm_reset_status_bridge.sv`
- `datasets/fixtures/dv/status_fifo.sv`

Current schema:

- `schemas/dataset/rtl-understanding.schema.json`

Current tasks:

- `clock_reset_extraction`
- `interface_extraction`
