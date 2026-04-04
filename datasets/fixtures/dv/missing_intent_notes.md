# Missing Intent Notes

- The block starts work when `enable` and `start` are asserted together.
- The author did not specify whether `done` must pulse for one cycle or stay high
  until acknowledged.
- The author did not specify whether back-to-back starts are required.
- No latency contract was provided beyond the visible RTL behavior.
