# AGENTS.md

## Project Purpose

This repository, `asic-ai-workflows`, is an open, structured collection of reusable
AI workflows for ASIC and semiconductor engineering.

The project goal is to replace ad-hoc prompts with:

- reusable skills
- reusable rules
- composable flows
- testable, reproducible engineering artifacts

The intended outcome is a practical, engineering-grade system that helps with real
chip-design and verification work, not generic prompt demos.

## Scope

This repository targets real semiconductor workflows, including:

- ASIC design
- design verification (DV)
- formal verification
- SoC integration
- static timing analysis (STA)
- lint
- synthesis
- physical design

## Core Model

The repository is organized around three building blocks:

- `skills/`: reusable AI tasks for specific engineering problems
- `rules/`: shared engineering constraints, domain knowledge, and grounding rules
- `flows/`: multi-step workflows that combine skills and rules

Agents working in this repo should preserve that separation:

- keep task-specific behavior in `skills/*/SKILL.md`
- keep reusable constraints and anti-hallucination policy in `rules/`
- put multi-step orchestration in `flows/`

## Current State

Current implemented skills:

- `skills/block-requirements-normalizer/`
- `skills/microarchitecture-spec-author/`
- `skills/rtl-designer/`
- `skills/rtl-lint-auditor/`
- `skills/rtl-rdc-auditor/`
- `skills/block-rtl-package-assembler/`
- `skills/rtl-cdc-linter/`
- `skills/rtl-timing-path-analyzer/`
- `skills/design-intent-to-dv-objectives/`
- `skills/rtl-verification-surface-extractor/`
- `skills/uvm-test-matrix-planner/`
- `skills/sva-candidate-planner/`
- `skills/functional-coverage-planner/`
- `skills/dv-plan-assembler/`

Current implemented rules:

- `rules/common/evidence-grounding.md`
- `rules/common/output-discipline.md`
- `rules/common/tool-evidence-provenance.md`
- `rules/arch/requirements-traceability.md`
- `rules/arch/ppa-capture.md`
- `rules/arch/diagram-selection.md`
- `rules/rtl/synthesizable-systemverilog.md`
- `rules/rtl/lint-severity.md`
- `rules/rdc/classification.md`
- `rules/cdc/classification.md`
- `rules/timing/register-evidence.md`
- `rules/dv/objective-traceability.md`
- `rules/dv/uvm-component-selection.md`
- `rules/dv/assertion-classification.md`
- `rules/dv/coverage-taxonomy.md`
- `rules/dv/stimulus-prioritization.md`

Current implemented flows:

- `flows/block-level-rtl-plan/`
- `flows/block-dv-plan/`

Current implemented schemas:

- `schemas/block-requirements.schema.json`
- `schemas/microarchitecture-spec.schema.json`
- `schemas/rtl-design.schema.json`
- `schemas/rtl-lint-report.schema.json`
- `schemas/rdc-report.schema.json`
- `schemas/block-rtl-package.schema.json`
- `schemas/cdc-report.schema.json`
- `schemas/timing-report.schema.json`
- `schemas/dv-objectives.schema.json`
- `schemas/rtl-verification-surface.schema.json`
- `schemas/uvm-test-plan.schema.json`
- `schemas/sva-plan.schema.json`
- `schemas/dv-coverage-plan.schema.json`
- `schemas/dv-plan.schema.json`

Current implemented smoke assets:

- `datasets/fixtures/rtl-plan/`
- `datasets/fixtures/cdc/`
- `datasets/fixtures/timing/`
- `datasets/fixtures/dv/`
- `evals/smoke/block-requirements-normalizer/`
- `evals/smoke/microarchitecture-spec-author/`
- `evals/smoke/rtl-designer/`
- `evals/smoke/rtl-lint-auditor/`
- `evals/smoke/rtl-rdc-auditor/`
- `evals/smoke/block-rtl-package-assembler/`
- `evals/smoke/rtl-cdc-linter/`
- `evals/smoke/rtl-timing-path-analyzer/`
- `evals/smoke/design-intent-to-dv-objectives/`
- `evals/smoke/rtl-verification-surface-extractor/`
- `evals/smoke/uvm-test-matrix-planner/`
- `evals/smoke/sva-candidate-planner/`
- `evals/smoke/functional-coverage-planner/`
- `evals/smoke/dv-plan-assembler/`

Current supporting files:

- `skills/rtl-timing-path-analyzer/default_config.yaml`
- `.github/workflows/ci.yml`
- `.github/pull_request_template.md`
- `scripts/repo_lint.py`
- `scripts/check_structured_files.py`
- `scripts/check_skill_contracts.py`
- `scripts/check_flow_contracts.py`
- `scripts/check_eval_smoke.py`
- `scripts/check_rtl_compile.py`
- `scripts/report_validators.py`

Important current limitation:

- The smoke-eval layer currently validates fixtures, schemas, metadata, and golden
  outputs; it does not yet execute live model runs.
- The DV flow is a planning workflow that emits structured verification plans. It
  does not generate runnable UVM infrastructure.

Current RTL compile policy:

- GitHub CI runs Verilator on every `.sv` and `.v` file in the repository.
- Multi-file RTL hierarchies must provide a `.f` filelist that captures the
  intended top-level compile unit and all required source files.
- GitHub CI also runs a `slang` frontend check on the same compile units.
- `slang` warnings are reported for visibility, but only `slang` errors fail CI.

## Source Of Truth

Use `README.md` as the high-level product and project source of truth.

Use the files under `skills/` and `rules/` as the source of truth for current
implemented behavior.

If `AGENTS.md` and `README.md` ever diverge, align work with `README.md` and update
`AGENTS.md` to match.

## Objectives For Agents

When contributing here, optimize for:

- engineering usefulness over presentation
- structured outputs over free-form prose
- deterministic behavior where possible
- evidence-grounded conclusions
- reusable artifacts instead of one-off prompts
- composability across skills, rules, and future flows

## Working Principles

Agents should follow these repo-specific principles:

1. Prefer real, working artifacts over speculative scaffolding.
2. Keep outputs structured and reproducible.
3. Avoid vague or marketing-style language in repository content.
4. Do not encode reusable policy in multiple skill files when it belongs in `rules/`.
5. Do not move domain-specific constraints into `rules/common/`; keep common rules
   genuinely generic.
6. Preserve deterministic schemas, enums, and naming once established.
7. When behavior is uncertain, prefer explicit uncertainty over invented detail.

## How To Approach Work

Before changing anything substantial:

1. Read `README.md`.
2. Inspect the relevant `skills/*/SKILL.md` and any referenced files.
3. Inspect the relevant `rules/*.md` files before modifying a skill that depends on them.
4. Verify the current tree instead of assuming planned directories or artifacts exist.

When adding or changing a skill:

1. Keep the skill narrowly scoped to a concrete engineering task.
2. Keep task flow, trigger conditions, and output schema in the skill file.
3. Move reusable grounding, classification, or policy rules into `rules/` only if
   they are likely to be shared across multiple skills or flows.
4. Prefer deterministic structured output formats.

When adding or changing a rule:

1. Put shared cross-domain rules in `rules/common/`.
2. Put domain-specific rules in a domain folder such as `rules/cdc/` or `rules/timing/`.
3. Avoid putting domain-specific constraints into `rules/common/`; keep common rules
   genuinely reusable across multiple domains.
4. Write rules as concrete, testable constraints, not abstract advice.

When adding new repo areas:

- follow the README build order as a default priority:
  1. create real, working skills
  2. validate with datasets
  3. add supporting rules
  4. compose flows

## Style Expectations

Repository content should be:

- concise
- technical
- explicit
- reusable
- testable

Avoid:

- unstructured prompts
- vague outputs
- unsupported claims
- duplicated policy across multiple files

## Practical Guidance For AI Agents

- Do not assume EDA-grade completeness when a skill explicitly describes itself as a
  pre-EDA or pre-synthesis lint/analysis pass.
- Do not claim more capability than the current skill or rule files support.
- If you rename or restructure artifacts, update all affected references in the repo.
- If you introduce a new shared policy, check whether it belongs in `rules/` rather
  than duplicating it across skills.

## Immediate Navigation Map

Start here for most tasks:

- `README.md`
- `flows/block-level-rtl-plan/FLOW.md`
- `flows/block-dv-plan/FLOW.md`
- `skills/block-requirements-normalizer/SKILL.md`
- `skills/microarchitecture-spec-author/SKILL.md`
- `skills/rtl-designer/SKILL.md`
- `skills/block-rtl-package-assembler/SKILL.md`
- `skills/rtl-cdc-linter/SKILL.md`
- `skills/rtl-timing-path-analyzer/SKILL.md`
- `skills/design-intent-to-dv-objectives/SKILL.md`
- `skills/dv-plan-assembler/SKILL.md`
- `rules/common/evidence-grounding.md`
- `rules/common/output-discipline.md`
- `rules/common/tool-evidence-provenance.md`
- `rules/arch/requirements-traceability.md`
- `rules/rtl/synthesizable-systemverilog.md`
- `rules/rdc/classification.md`
- `rules/cdc/classification.md`
- `rules/timing/register-evidence.md`
- `rules/dv/objective-traceability.md`

## Contribution Standard

A good contribution in this repo should make the repository more:

- accurate
- reusable
- deterministic
- composable
- aligned with real semiconductor engineering workflows
