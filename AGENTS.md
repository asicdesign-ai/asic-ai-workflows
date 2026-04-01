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

- `skills/rtl-cdc-linter/`
- `skills/rtl-timing-path-analyzer/`

Current implemented rules:

- `rules/common/evidence-grounding.md`
- `rules/common/output-discipline.md`
- `rules/cdc/classification.md`
- `rules/timing/register-evidence.md`

Current supporting files:

- `skills/rtl-timing-path-analyzer/default_config.yaml`

Important current limitation:

- `flows/`, `schemas/`, and `datasets/` are described in the README vision, but are
  not yet present in this clone. Do not assume they already exist.

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
- `skills/rtl-cdc-linter/SKILL.md`
- `skills/rtl-timing-path-analyzer/SKILL.md`
- `rules/common/evidence-grounding.md`
- `rules/common/output-discipline.md`
- `rules/cdc/classification.md`
- `rules/timing/register-evidence.md`

## Contribution Standard

A good contribution in this repo should make the repository more:

- accurate
- reusable
- deterministic
- composable
- aligned with real semiconductor engineering workflows
