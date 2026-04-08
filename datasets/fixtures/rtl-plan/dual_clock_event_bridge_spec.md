# Dual Clock Event Bridge Microarchitecture

## Overview

`dual_clock_event_bridge` transfers an event pulse from `src_clk_i` into
`dst_clk_i` using a source toggle and destination edge detect structure.

## Interfaces

- `src_clk_i`
- `src_rst_n`
- `src_event_i`
- `dst_clk_i`
- `dst_rst_n`
- `dst_event_o`

## Timing Intent

- source toggles a bit on each accepted source event
- destination resynchronizes the toggle and pulses `dst_event_o` on edge detect

## Notes

- back-to-back event limits depend on the destination synchronizer latency
