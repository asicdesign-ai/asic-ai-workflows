---
name: rtl-lint-auditor
description: >
  Review synthesizable SystemVerilog for static RTL issues such as inferred
  latches, reset mismatches, width hazards, and multi-driver structure. Use this
  skill whenever generated RTL needs a deterministic front-end lint audit before
  CDC, RDC, or timing review.
---

# RTL Lint Auditor Skill

Audit block-level SystemVerilog for front-end lint issues and emit one
deterministic finding report.

Scope: block or small IP. This is a static lint audit, not an EDA signoff run.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/rtl/synthesizable-systemverilog.md`
- `../../rules/rtl/lint-severity.md`

## Analysis

Read the RTL and perform these steps:

1. Identify structural lint issues that can be proven from the provided code.
2. Classify each issue with the severity mapping in
   `../../rules/rtl/lint-severity.md`.
3. Mark `critical` and `high` findings as blocking.
4. Suggest the smallest valid fix for blocking issues.
5. Emit an empty `findings` list when the RTL is clean under this rule set.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: event_counter
  rtl_files:
    - rtl/event_counter.sv

findings:
  - id: LINT-001
    severity: high
    category: latch
    file: rtl/event_counter.sv
    line: 27
    message: "The combinational next-state block leaves irq_nxt unassigned on one branch."
    recommendation: "Assign irq_nxt on every path or provide a default assignment before the branch tree."
    blocking: true

summary:
  total_findings: 1
  blocking_findings: 1
  by_severity:
    critical: 0
    high: 1
    medium: 0
    low: 0
    info: 0
```

## Scope Limitations

- **Can do**: flag code-local lint hazards grounded in the RTL text.
- **Cannot do**: replace full lint tool rule decks, prove CDC safety, or prove
  implementation timing.
