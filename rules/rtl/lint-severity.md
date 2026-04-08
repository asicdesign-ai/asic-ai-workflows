# Lint Severity

Use this rule whenever a skill emits static RTL lint findings.

## Severity Mapping

- `critical`: Multiple drivers, combinational loops, or structurally unsafe code
  that blocks further design use.
- `high`: Inferred latches, reset mismatches on state, width truncation on
  architecturally visible signals, or similar issues that require RTL changes.
- `medium`: Style or robustness issues that should be fixed before wider reuse
  but do not block initial planning.
- `low`: Minor consistency issues with limited behavioral risk.
- `info`: Non-blocking observations.

## Required behavior

1. Classify each finding using the smallest justified severity.
2. Mark `critical` and `high` findings as blocking.
3. Ground each finding in a file path, line number, and short factual message.
4. Suggest the smallest valid fix for blocking findings.

## Prohibited behavior

- Do not mark stylistic preferences as `critical` or `high`.
- Do not omit the blocking flag for `critical` or `high` findings.
