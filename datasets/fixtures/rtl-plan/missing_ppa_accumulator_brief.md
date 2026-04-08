# Missing PPA Accumulator Brief

Design a small accumulator block for a sensor front end.

Requirements:

- accumulate `sample_i[11:0]` values while `enable_i` is high
- clear on reset or `clear_i`
- expose the current accumulated value on `sum_o[15:0]`

No explicit power, performance, or area targets are provided.
