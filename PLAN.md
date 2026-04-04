# PLAN

## Goal

Develop a practical system of AI "engineer" workflows for ASIC and semiconductor
work that stays aligned with this repository's structure:

- `skills/` for narrow reusable engineering tasks
- `rules/` for shared grounding and domain constraints
- `flows/` for multi-step orchestration across skills and rules
- `scripts/` for deterministic validation, execution harnesses, and report tooling

## Recommendation

Proceed with `flows/`, but keep the first flow implementations thin and concrete.

Do not model broad engineer personas as single monolithic skills. Roles such as
chip architect, RTL designer, CDC expert, STA expert, and DFT expert should be
represented primarily as flows that compose multiple narrow skills.

Use scripts to support execution and validation, not to hold the engineering
reasoning itself.

## Artifact Mapping

### Skills

Use skills for specific engineering tasks with deterministic structured outputs.

Examples:

- `rtl-cdc-linter`
- `rtl-timing-path-analyzer`
- `rtl-reset-rdc-auditor`
- `rtl-dft-scanability-auditor`
- `scan-insertion-planner`
- `mbist-wrapper-planner`
- `rtl-lint-warning-explainer`
- `sva-property-extractor`

### Rules

Use rules for reusable grounding, classification, and output constraints shared
across multiple skills and flows.

Examples:

- shared evidence-grounding and output-discipline rules
- CDC classification rules
- timing register-evidence rules
- future DFT, reset/RDC, and protocol-audit rules

### Flows

Use flows for role-level or mission-level compositions of skills.

Examples:

- `pre-synthesis-rtl-audit`
- `chip-architecture-review`
- `rtl-design-bringup`
- `soc-interface-integration-review`
- `dft-readiness-review`

### Scripts

Use scripts for deterministic repository support functions only.

Examples:

- flow runners
- schema validation
- report merging
- smoke-eval execution
- regression comparison

## Role Decomposition

Treat each "engineer" as a flow built from smaller skills.

### Chip Architect

Prefer a flow over skills such as:

- requirements extraction
- block partitioning
- interface definition
- clock and reset planning
- memory map planning

### RTL Designer

Prefer a flow over skills such as:

- RTL skeleton generation
- FSM extraction or construction
- datapath and control partitioning
- assertion stub generation
- interface glue generation

### CDC Expert

Model as a skill family and reuse in audit flows.

### STA Expert

Model as a skill family and reuse in audit flows.

### DFT Expert

Split into multiple skills rather than one broad skill.

Recommended initial DFT skill split:

- `rtl-dft-scanability-auditor`
- `scan-insertion-planner`
- `mbist-wrapper-planner`

If code transformation is added later:

- `rtl-scan-wrapper-generator`

## Additional Engineer Ideas

- reset/RDC expert
- lint and style expert
- SVA or property extraction expert
- DV test-planning expert
- SoC integration and interface expert
- AXI/APB protocol audit expert
- SDC or constraint review expert
- SRAM and ECC integration expert

## Recommended Build Order

Follow a skill-first, validation-first sequence:

1. Add 2-4 more narrow audit or planning skills.
2. Add domain rules needed by those skills.
3. Add one initial flow in `flows/`.
4. Add flow-level schemas, fixtures, and smoke validation.
5. Add broader generative design flows only after the audit and planning layer is
   strong enough to support them.

## First Flow Recommendation

Implement `flows/pre-synthesis-rtl-audit/` first.

Suggested flow steps:

1. run CDC audit
2. run timing audit
3. run reset/RDC audit
4. run DFT scanability audit
5. merge findings into one structured report

This creates a practical "team of engineers" workflow while staying consistent
with the repository's current emphasis on narrow skills, shared rules, and
testable outputs.
