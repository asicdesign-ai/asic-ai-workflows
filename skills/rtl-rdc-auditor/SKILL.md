---
name: rtl-rdc-auditor
description: >
  Audit RTL for reset-domain crossing hazards that are separate from clock-domain
  crossings. Use this skill whenever a design has multiple resets, asynchronous
  reset release behavior, or reset-bridged control paths that need structured
  review.
---

# RTL RDC Auditor Skill

Analyze block-level SystemVerilog for reset-domain crossing hazards and emit one
structured RDC report.

Scope: block or small IP. This is a pre-EDA RDC audit, not a replacement for
dedicated signoff tools.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/rdc/classification.md`

## Analysis

Read the RTL and perform these steps:

1. Identify visible reset domains from sequential logic and reset control paths.
2. Detect when logic governed by one reset domain is sampled or consumed in
   logic governed by a different reset domain.
3. Classify protection status and severity using
   `../../rules/rdc/classification.md`.
4. Suggest the smallest valid fix for medium-or-higher findings.
5. Keep RDC findings separate from CDC findings.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: event_counter
  rtl_files:
    - rtl/event_counter.sv

reset_domains:
  - name: rst_n
    active: active_low
    style: async
    line: 11

crossings:
  - id: RDC-001
    signal: irq_hold
    source_reset: cfg_rst_n
    dest_reset: rst_n
    line: 42
    protected: false
    severity: high
    description: "irq_hold is released by cfg_rst_n and sampled in logic released by rst_n without a visible reset bridge."
    fix: "Stage the release into the destination reset domain or add an explicit reset bridge."

summary:
  total_crossings: 1
  violations: 1
  by_severity:
    critical: 0
    high: 1
    medium: 0
    low: 0
    info: 0
```

## Scope Limitations

- **Can do**: identify reset-domain hazards visible in the provided RTL.
- **Cannot do**: prove power-domain behavior, replace formal RDC signoff, or
  infer missing reset intent.
