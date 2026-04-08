---
name: microarchitecture-spec-author
description: >
  Turn normalized block requirements into a Markdown microarchitecture
  specification with requirement traceability and targeted diagrams. Use this
  skill whenever the workflow needs a deterministic architecture document before
  RTL generation.
---

# Microarchitecture Spec Author Skill

Generate one Markdown microarchitecture specification from normalized block
requirements.

Scope: block or small IP. This is a specification skill, not an RTL or signoff
tool.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/arch/requirements-traceability.md`
- `../../rules/arch/ppa-capture.md`
- `../../rules/arch/diagram-selection.md`

## Analysis

Read the normalized requirements and perform these steps:

1. Draft a Markdown microarchitecture spec with clear sections for overview,
   interfaces, clocks/resets, datapath/control, PPA notes, and unresolved items.
2. Trace each requirement into one or more spec sections.
3. Add WaveDrom only for timing relationships, Mermaid only for FSMs, and
   BlockDiag only for structural block views.
4. Keep the spec grounded in explicit requirements and emitted open questions.
5. Carry unresolved items forward instead of inventing microarchitectural detail.

## Output Format

Produce a single YAML document:

```yaml
design:
  top_module: event_counter
  brief_summary: "Programmable event counter with optional interrupt threshold."

requirements_trace:
  - requirement_id: REQ-001
    spec_sections:
      - overview
      - datapath
    coverage: full

artifact:
  path: artifacts/microarchitecture/event_counter.md
  format: markdown

spec_markdown: |
  # Event Counter Microarchitecture

  ## Overview
  This block counts qualified input events and raises an optional threshold interrupt.

diagrams:
  - tool: blockdiag
    title: block partitioning
    purpose: block_diagram
    artifact_path: artifacts/microarchitecture/diagrams/event_counter_blockdiag.diag
    content: "blockdiag { counter_if -> counter_core -> irq_logic; }"

unresolved:
  - item: threshold clear policy
    reason: "The intake does not define whether irq clears automatically or only by software."
    blocking: true
    requirement_ids:
      - REQ-001

summary:
  total_traced_requirements: 1
  total_diagrams: 1
  total_unresolved: 1
```

## Scope Limitations

- **Can do**: generate a traceable Markdown architecture spec with targeted
  diagrams and unresolved items.
- **Cannot do**: choose unsupported system behavior, prove timing closure, or
  replace the downstream RTL review loop.
