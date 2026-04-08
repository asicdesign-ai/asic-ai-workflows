---
name: block-rtl-package-assembler
description: >
  Assemble normalized requirements, the microarchitecture spec, generated RTL,
  and static audit summaries into one front-end handoff package. Use this skill
  whenever the block-level RTL planning flow needs one deterministic output that
  can feed downstream DV planning.
---

# Block RTL Package Assembler Skill

Merge the front-end planning artifacts into one block-level RTL handoff package.

Scope: block or small IP. This is a package assembly skill, not a DV or physical
implementation flow.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/arch/requirements-traceability.md`
- `../../rules/arch/ppa-capture.md`

## Analysis

Read the normalized requirements, spec artifacts, RTL design artifacts, and
audit reports, then perform these steps:

1. Preserve the `REQ-NNN` requirement namespace throughout the final package.
2. Summarize the spec and RTL manifests without dropping traceability.
3. Roll lint, CDC, RDC, and timing into one audit summary with a single DV
   handoff readiness flag.
4. Preserve unresolved or blocked items instead of claiming closure.
5. Emit downstream handoff metadata for `block-dv-plan`.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: event_counter
  brief_summary: "Programmable event counter with optional interrupt threshold."
  rtl_files:
    - rtl/event_counter.sv

requirements:
  - id: REQ-001
    title: count qualified input events
    category: function
    priority: must
    source: user
    description: "The block increments a stored count when event_valid is asserted."
    acceptance_criteria: "With counting enabled, each qualified event increments count_value by one."

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
    target: "small control block"
    units: null
    priority: "secondary"
    status: qualitative

spec:
  artifact_path: artifacts/microarchitecture/event_counter.md
  requirements_trace:
    - requirement_id: REQ-001
      spec_sections:
        - overview
        - datapath
      coverage: full
  diagrams: []

rtl:
  source_files:
    - path: rtl/event_counter.sv
      module: event_counter
      language: systemverilog
      content: "module event_counter; endmodule"
  rtl_modules:
    - name: event_counter
      role: top
      clocks:
        - clk
      resets:
        - rst_n
      description: "Counts qualified events and exposes the stored count."
  traceability:
    - requirement_id: REQ-001
      spec_sections:
        - datapath
      rtl_files:
        - rtl/event_counter.sv
      rtl_signals:
        - event_valid
        - count_value

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
    deepest_path_depth: 4
  ready_for_dv_handoff: true

unresolved: []

downstream_handoff:
  recommended_flow: block-dv-plan
  top_module: event_counter
  rtl_files:
    - rtl/event_counter.sv
  design_intent_markdown: artifacts/microarchitecture/event_counter.md
  notes: "Use the generated microarchitecture spec as the design-intent brief for the downstream DV planning flow."

summary:
  total_requirements: 1
  total_rtl_files: 1
  total_blocking_issues: 0
  total_unresolved: 0
```

## Scope Limitations

- **Can do**: produce one deterministic front-end handoff package with
  traceability and audit summaries.
- **Cannot do**: replace the downstream DV flow, claim synthesis closure, or
  claim signoff completeness.
