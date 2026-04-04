
# asic-ai-workflows

Open, structured repository of reusable AI workflows for ASIC and semiconductor engineering.

---

## Overview

This project aims to build a **practical, engineering-grade system of AI workflows** for chip design and verification.

The repository is organized around three core building blocks:

- **Skills** — reusable AI tasks for specific engineering problems  
- **Rules** — domain knowledge and constraints  
- **Flows** — multi-step workflows combining skills and rules  

The goal is to move from ad-hoc prompts to **structured, reusable, and testable AI artifacts**.

---

## Scope

This repository targets real-world semiconductor workflows, including:

- ASIC Design  
- Design Verification (DV)  
- Formal Verification  
- SoC Integration  
- Static Timing Analysis (STA)  
- Lint  
- Synthesis  
- Physical Design  

---

## Repository Structure

- `skills/` — Reusable AI engineering skills  
- `rules/` — Static domain knowledge and constraints  
- `flows/` — Multi-step engineering workflows  
- `schemas/` — Standardized definitions for all artifacts  
- `datasets/` — Example inputs for testing and validation  

Each component has a clear responsibility and is designed to be composable.

Current repository contents:

- `skills/rtl-cdc-linter/` — Pre-EDA RTL CDC lint skill  
- `skills/rtl-timing-path-analyzer/` — Pre-synthesis RTL timing path analysis skill  
- `skills/design-intent-to-dv-objectives/` — Block-level DV objective planning skill
- `skills/rtl-verification-surface-extractor/` — Block-level verification surface extraction skill
- `skills/uvm-test-matrix-planner/` — UVM-centric DV test planning skill
- `skills/sva-candidate-planner/` — Block-level assertion candidate planning skill
- `skills/functional-coverage-planner/` — Block-level coverage planning skill
- `skills/dv-plan-assembler/` — Final DV plan assembly skill
- `rules/common/evidence-grounding.md` — Shared anti-hallucination grounding rule  
- `rules/common/output-discipline.md` — Shared structured-output rule  
- `rules/cdc/classification.md` — CDC synchronizer proof and severity mapping  
- `rules/timing/register-evidence.md` — Timing register proof and unresolved-object handling  
- `rules/dv/` — Block-level DV planning and traceability rules
- `flows/block-dv-plan/` — Block-level, UVM-centric DV planning flow
- `schemas/` — Report schemas for the currently implemented skills and DV flow artifacts  
- `datasets/fixtures/` — RTL smoke fixtures for CDC, timing, and DV planning  
- `evals/smoke/` — Smoke-eval metadata and golden outputs for current skills and DV plan artifacts  
- `scripts/` — Local and CI validation scripts for repo structure and smoke assets  
- `.github/workflows/ci.yml` — Bootstrap CI checks for repo lint, skill contracts, flow contracts, and smoke assets  

---

## Design Principles

This project follows a set of practical design principles:

- Focus on real engineering problems  
- Prefer structured, reusable artifacts over ad-hoc prompts  
- Ensure outputs are testable and reproducible  
- Build composable workflows from simple components  
- Prioritize functionality over presentation  

These principles guide the development of skills, rules, and flows.

---

## What is a Skill?

A **skill** is a reusable AI capability that solves a specific engineering task.

Current skills:

- RTL Timing Path Analyzer  
- RTL CDC Linter  
- Design Intent To DV Objectives
- RTL Verification Surface Extractor
- UVM Test Matrix Planner
- SVA Candidate Planner
- Functional Coverage Planner
- DV Plan Assembler

Planned examples:

- Lint Warning Explainer  
- Simulation Failure Analyzer  
- UVM Test Generator  

Each skill is:

- Structured  
- Deterministic (as much as possible)  
- Backed by real examples  
- Designed for reuse across flows  

---

## What is a Rule?

A **rule** encodes domain knowledge or engineering best practices.

Rules in this repository are used to reduce hallucination and improve determinism by
separating reusable constraints from task-specific skill instructions.

Current examples:

- `rules/common/evidence-grounding.md` — require explicit RTL evidence for every claim
- `rules/common/output-discipline.md` — enforce stable YAML shape and field usage
- `rules/cdc/classification.md` — define what counts as a proven CDC synchronizer
- `rules/timing/register-evidence.md` — define when a timing object is trusted vs unresolved

Rules are used by:
- Skills
- Flows
- Agents

Current validation approach:

- repo-structure linting
- JSON and YAML syntax checks
- skill contract checks
- flow contract checks
- schema-backed smoke-eval asset validation

The current smoke layer validates fixtures, metadata, and golden outputs. It does
not yet execute live LLM runs against the corpus.

---

## What is a Flow?

A **flow** is a multi-step workflow that combines skills and rules.

Example: Timing Closure Flow

1. Run STA  
2. Extract worst paths  
3. Classify violations  
4. Suggest fixes  
5. Re-run timing  

Current implemented flow:

- `block-dv-plan` — derive DV objectives, extract the verification surface, plan
  UVM tests/assertions/coverage, and assemble one final structured DV plan with
  optional CDC and timing risks

---

## Development Strategy

The project follows a strict build order:

1. Create real, working skills  
2. Validate with datasets  
3. Add supporting rules  
4. Compose flows   


---

## Long-Term Vision

Build the largest open repository of:

> **AI-powered semiconductor engineering workflows**

Target users:

- ASIC engineers  
- DV engineers  
- Physical design engineers  
- SoC architects  
- Formal engineers  

---

## Contributing

Contributions are welcome, but must follow:

- Defined schemas  
- Structured formats  
- Engineering-grade quality  
- Reproducible examples  

Avoid:
- Unstructured prompts  
- Vague outputs  

---

## License

MIT License

---

## Future

Planned extensions:

- Skill chaining  
- Automated flow execution  
- Dataset benchmarking  
- Prompt optimization  
- Model comparison  

---
