# Pull Request Governance And Quality Plan

## Goal

Move this repository from direct pushes on `main` to a pull-request-based workflow,
and add enough automated validation that changes to skills, rules, schemas, and
smoke assets do not silently degrade current behavior.

## Current Repository Reality

This repository currently contains:

- repo documentation
- two implemented skills
- four implemented rules
- one timing config file

It does not yet contain flow implementations, a full model-eval harness, or a
runtime application. That means the first quality gates should focus on:

- repository structure integrity
- skill and rule contract integrity
- schema validity
- smoke-eval asset integrity

## Branch Protection Plan

Preferred mechanism:

1. Use a GitHub ruleset targeting `main` if the repository plan supports it.
2. If rulesets are unavailable for this repository type, use classic branch
   protection on `main`.

Required settings for `main`:

- require a pull request before merging
- require status checks to pass before merging
- require conversation resolution before merging
- require linear history
- block force pushes
- block branch deletion

Recommended merge policy:

- allow squash merge
- disable direct pushes to `main`
- avoid merge commits on `main`

Review policy rollout:

1. Phase A: require pull requests, but do not require approvals if there is only
   one active maintainer.
2. Phase B: once there is a second maintainer, require at least one approval,
   dismiss stale approvals, and require approval for the most recent push.
3. Phase C: add `CODEOWNERS` and require code-owner review once ownership is
   meaningful and there are real reviewers for the affected areas.

## Required Status Checks

Target required checks once the workflow is stable:

- `repo-lint`
- `skill-contracts`
- `eval-smoke`

Important:

- Keep the job names stable once branch protection depends on them.
- Do not duplicate required check names across workflows.

## Step 1 Implementation Scope

Step 1 is the bootstrap phase. It should add the scaffolding needed before strict
branch protection is turned on.

Deliverables:

- `.github/workflows/ci.yml`
- `.github/pull_request_template.md`
- `schemas/` for current skill outputs
- `datasets/fixtures/` for current smoke cases
- `evals/smoke/` metadata and expected outputs
- `scripts/` for local and CI validation

Step 1 should not claim full model-regression coverage yet. It should provide the
asset structure and validation hooks needed to grow into that coverage.

## Quality Gate Design

### 1. repo-lint

Purpose:

- catch broken repo structure and broken documentation links early

Checks:

- no empty `README.md` files
- valid JSON files
- valid local markdown links
- expected top-level repo files remain present

### 2. skill-contracts

Purpose:

- keep skill files and rule references structurally valid

Checks:

- every skill directory contains `SKILL.md`
- skill frontmatter contains `name` and `description`
- referenced rule paths exist
- `Output Format` includes a fenced YAML example block
- `default_config.yaml` exists where referenced and contains the expected top-level
  sections for the timing skill

### 3. eval-smoke

Purpose:

- protect the current skills and rules from silent degradation

Bootstrap checks for step 1:

- every smoke case has metadata
- every metadata file points to existing fixtures, schemas, and expected outputs
- every schema file is valid JSON
- every expected output conforms to the current structural validator for that skill

Future expansion after step 1:

- execute the actual skill against fixtures
- compare produced outputs to expected outputs and assertions
- gate merges on baseline pass rate versus `main`

## Initial Smoke Coverage

### RTL CDC Linter

The smoke suite should cover at least:

- unsynchronized single-bit crossing
- explicit 2-FF synchronizer
- naming-only synchronizer trap
- deduplicated multi-consumer crossing

### HDL Design View Extractor

The smoke suite should cover at least:

- SystemVerilog source converted into a model-derived design view
- proprietary HDL-like source converted into a confidence-limited design view

### RTL Timing Analyzer

The smoke suite should cover at least:

- simple reg-to-reg hard path
- unresolved FF-like macro or cell
- cross-module timing path when all modules are provided

## Unit-Test Strategy For This Repository

This repository is mostly structured prompt, rule, and artifact content. For that
reason, "unit tests" should focus on deterministic contracts rather than runtime
business logic.

Recommended test layers:

1. file-structure tests
2. schema validation tests
3. skill contract tests
4. smoke-eval asset tests
5. later, live model regression tests

## Linter Strategy

Recommended eventual additions:

- markdown linting for all `.md` files
- YAML linting for workflow and config files
- link checking for local docs links

Step 1 does not need to adopt external lint tools if local scripts provide enough
signal to bootstrap CI. External linters can be layered in later.

## Rollout Order

1. Add CI, schemas, fixtures, smoke assets, and validation scripts.
2. Run the checks on `main` until they are stable.
3. Turn those checks into required status checks on `main`.
4. Enforce pull requests for `main`.
5. Add required approvals when reviewer capacity exists.
6. Add code-owner review when repo ownership is mature enough.

## Residual Risks After Step 1

Even after step 1 lands:

- the smoke suite will validate assets, not live model behavior
- there will still be no automatic semantic comparison between current outputs and
  previous model outputs
- branch protection will still need to be configured in GitHub settings manually

## Follow-Up Work After Step 1

- add `CODEOWNERS` when reviewer ownership is real
- add live eval execution against the smoke corpus
- add larger nightly eval coverage
- add dataset expansion for more domains as new skills land
- add flows and flow-level validation when the repository reaches that stage

## Reference Documentation

- GitHub rulesets:
  https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- Available rules for rulesets:
  https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- Protected branches:
  https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- CODEOWNERS:
  https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
