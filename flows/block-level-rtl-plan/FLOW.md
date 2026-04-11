---
name: block-level-rtl-plan
description: >
  Build a block-level front-end RTL package from a high-level design brief,
  explicit PPA intake, a Markdown microarchitecture spec, generated RTL, and
  static audit passes. Use this flow whenever the user wants to move from
  block intent into traceable RTL artifacts and a downstream DV handoff.
---

# Block Level RTL Plan Flow

Build one front-end RTL package for a block or small IP from microarchitectural
intent, explicit PPA targets, generated RTL, and static audit feedback.

## Inputs

- `top_module`
- `design_brief`
- optional `existing_rtl_files[]`
- optional `interface_requirements`
- optional `clock_reset_requirements`
- optional `process_or_node`
- `ppa_targets.performance`
- `ppa_targets.power`
- `ppa_targets.area`

## Trigger Phrases

Use this flow when the user asks for front-end block planning with phrases such
as:

- `block-level RTL plan`
- `microarchitecture to RTL`
- `generate a microarchitecture spec`
- `turn requirements into RTL`
- `front-end RTL closure`
- `act as an RTL designer`
- `derive RTL from architecture`
- `prepare a DV handoff package`

Example requests:

- "Create a block-level RTL plan from this microarchitectural brief."
- "Write a microarchitecture spec and draft RTL for this block."
- "Capture PPA, propose the architecture, generate RTL, and audit it."
- "Take this block intent through front-end RTL readiness."

## Rules

Apply these repo rules across the flow:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/arch/requirements-traceability.md`
- `../../rules/arch/ppa-capture.md`
- `../../rules/arch/diagram-selection.md`
- `../../rules/rtl/synthesizable-systemverilog.md`
- `../../rules/rtl/lint-severity.md`
- `../../rules/rdc/classification.md`

## Skills

Run these skills in order:

1. `../../skills/block-requirements-normalizer/SKILL.md`
2. `../../skills/microarchitecture-spec-author/SKILL.md`
3. `../../skills/rtl-designer/SKILL.md`
4. `../../skills/rtl-lint-auditor/SKILL.md`
5. `../../skills/rtl-cdc-linter/SKILL.md`
6. `../../skills/rtl-rdc-auditor/SKILL.md`
7. `../../skills/rtl-timing-path-analyzer/SKILL.md`
8. `../../skills/block-rtl-package-assembler/SKILL.md`

## Execution

1. Normalize the design brief into deterministic `REQ-NNN` requirements and
   explicit `power`, `performance`, and `area` targets.
2. If any PPA target is missing, emit blocking intake questions before claiming
   specification readiness.
3. Draft the microarchitecture specification in Markdown and use WaveDrom,
   Mermaid, or BlockDiag only when they clarify timing, FSM, or block structure.
4. Generate synthesizable SystemVerilog from the approved spec.
5. Audit the emitted RTL with lint, timing-risk analysis, and applicable CDC or
   RDC review.
6. Skip CDC when the visible RTL contains only one clock domain. In that case,
   emit a zero-crossing CDC report rather than forcing a multi-clock audit.
7. Skip RDC when all sequential state uses one reset signal with one consistent
   reset style and polarity. If the same reset signal is mixed between
   synchronous and asynchronous reset styles, still run RDC and treat those
   style differences as distinct reset domains.
8. Re-run `rtl-designer` after any `critical` or `high` lint, CDC, or RDC
   result until the issue is fixed or explicitly carried as unresolved.
9. Treat timing as advisory unless the reported structure clearly forces a
   redesign.
10. Assemble one final handoff package and mark whether it is ready for
   downstream `block-dv-plan` use.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: event_counter
  brief_summary: "Programmable event counter with optional interrupt threshold."
  rtl_files:
    - rtl/event_counter.sv

requirements: []

ppa_targets:
  performance:
    target: "600"
    units: "MHz"
    priority: "primary"
    status: numeric
  power:
    target: "minimize dynamic power"
    units: null
    priority: "secondary"
    status: qualitative
  area:
    target: null
    units: null
    priority: "secondary"
    status: missing

spec:
  artifact_path: artifacts/microarchitecture/event_counter.md
  requirements_trace: []
  diagrams: []

rtl:
  source_files: []
  rtl_modules: []
  traceability: []

audit_summary:
  lint:
    total_findings: 0
    blocking_findings: 0
  cdc:
    violations: 0
    highest_severity: none
  rdc:
    violations: 0
    highest_severity: none
  timing:
    hard_or_worse_paths: 0
    deepest_path_depth: 0
  ready_for_dv_handoff: false

unresolved: []

downstream_handoff:
  recommended_flow: block-dv-plan
  top_module: event_counter
  rtl_files:
    - rtl/event_counter.sv
  design_intent_markdown: artifacts/microarchitecture/event_counter.md
  notes: "Use the generated microarchitecture spec as the design-intent brief for block-dv-plan."

summary:
  total_requirements: 0
  total_rtl_files: 0
  total_blocking_issues: 0
  total_unresolved: 0
```

## Scope Limitations

- **Can do**: capture block intent, PPA intake, architecture, RTL generation,
  static front-end audits, and DV handoff metadata.
- **Cannot do**: generate signoff claims, replace synthesis or place-and-route,
  or plan SoC-level implementation closure.
