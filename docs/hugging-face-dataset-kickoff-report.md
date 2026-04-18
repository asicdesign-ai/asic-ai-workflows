# Hugging Face Dataset Kickoff Report

## Purpose

This report explains, in simple words, what was done in this session to start a
real Hugging Face dataset effort inside `asic-ai-workflows`.

The audience is an ASIC engineer, so the language is kept simple, but the
content stays engineering-focused.

## Short Answer

We did **not** build a full dataset yet.

We did the correct first engineering work:

- cleaned up the dataset plan
- made the plan match the repo's real structure and CI rules
- created the first dataset schema
- created the first real dataset record from an existing RTL fixture

In other words:

This session moved the repo from **"dataset idea"** to **"first concrete dataset artifact"**.

## What Was In The Repo At The Start

Two new Markdown plans had been added:

- `hugging_face_for_asic_plan.md`
- `full_rtl_dataset_plan.md`

These documents had good intent, but they were still too high-level for this
repository.

Main problems in the original drafts:

- too much strategy language, not enough execution detail
- no strong provenance and licensing contract
- no clean train/validation/test split policy
- no compile-unit handling for real RTL hierarchies
- no explanation of how bad RTL should coexist with this repo's CI checks
- "good vs bad RTL" was too vague as a dataset target

## What I Changed

### 1. Audited and rewrote the two plan documents

I revised both plan files so they now match the repo's engineering style and
constraints.

Key changes:

- Hugging Face is now defined as the **distribution layer**
- this repo stays the **source of truth**
- the first release is limited to **front-end RTL**, not all ASIC data
- the first tasks are **deterministic extraction/classification tasks**
- every dataset record must carry **schema, provenance, license, and split metadata**
- dataset release should be **small, clean, and benchmark-friendly**

### 2. Fixed the typo in the plan filename

The file originally named `full_rtl_dataest_plan.md` was renamed to:

- `full_rtl_dataset_plan.md`

This removed the typo and made the path easier to understand.

### 3. Created the first dataset schema area

I added a new schema directory:

- `schemas/dataset/`

New files:

- `schemas/dataset/rtl-record-common.schema.json`
- `schemas/dataset/rtl-understanding.schema.json`

What these do:

- define the common record contract
- define the first task-specific contract
- create a stable shape for future dataset records

### 4. Chose one narrow first task

Instead of trying to create a broad dataset immediately, I started with one
small and deterministic task:

- `clock_reset_extraction`

This is a good first task because:

- the labels are concrete
- the answer can be grounded in RTL text
- it matches front-end design review work
- it is easier to validate than free-form summaries

### 5. Created the first real dataset record

I created the first canary dataset record under:

- `datasets/corpora/rtl-understanding-v1/`

Main files:

- `datasets/corpora/rtl-understanding-v1/README.md`
- `datasets/corpora/rtl-understanding-v1/cases/single-clock-controller-clock-reset-extraction/record.json`
- `datasets/corpora/rtl-understanding-v1/cases/single-clock-controller-clock-reset-extraction/provenance.yaml`

This record uses an existing repo fixture:

- `datasets/fixtures/rtl-plan/single_clock_controller.sv`

The record says, in structured form:

- top module is `single_clock_controller`
- clock is `clk_i`
- reset is `rst_n`
- reset is active-low
- reset style is asynchronous

It also includes **evidence lines** pointing back to the actual RTL.

This is important: the record is not just labeled, it is **evidence-grounded**.

### 6. Updated repo documentation so the new dataset work is visible

I updated these files:

- `README.md`
- `AGENTS.md`
- `CONTRIBUTING.md`

Why:

- to make `schemas/dataset/` an official repo area
- to make `datasets/corpora/` an official repo area
- to avoid hidden structure that only exists in files but not in repo docs

## Important Engineering Decisions

### Hugging Face is not the factory

The repo should generate, validate, and version the data.

Hugging Face should only be the place where the final dataset snapshot is
published.

Why this matters:

- better reproducibility
- better review
- better control of provenance
- better alignment with this repo's structured workflow model

### Start with front-end RTL, not all ASIC data

The first release should stay in the area where labels are practical and useful:

- interface extraction
- clock/reset extraction
- state element inventory
- structured RTL quality labeling

Do not start with:

- place-and-route data
- signoff timing claims
- unstructured EDA logs
- vague "all ASIC" datasets

### A good dataset row is a task, not a file dump

Bad approach:

- upload many Verilog files

Good approach:

- define a task
- define the input
- define the gold output
- define the metadata
- define the provenance

This is the difference between a file archive and a useful benchmark.

### Bad RTL must respect repo CI

This repo compiles checked-in `.sv` and `.v` files in CI.

That means intentionally broken RTL cannot be added casually as normal source
files if it may fail compile.

So the plan now says:

- compile-clean RTL can live as normal checked-in fixtures
- intentionally bad RTL can live as text inside dataset records or other
  non-compiled artifacts

This is a very important repo-specific constraint.

### Split hygiene matters from the beginning

The plan now requires split-by-lineage, not random row shuffling.

Meaning:

- similar mutations of the same base module should stay in the same split
- near-duplicates should not leak across train and test
- test data should include truly unseen families when possible

For an ASIC engineer, this is the dataset version of avoiding false coverage
closure.

## New Files Added

### Plan and documentation

- `hugging_face_for_asic_plan.md`
- `full_rtl_dataset_plan.md`
- `docs/hugging-face-dataset-kickoff-report.md`

### Schema files

- `schemas/dataset/rtl-record-common.schema.json`
- `schemas/dataset/rtl-understanding.schema.json`

### Dataset seed files

- `datasets/corpora/rtl-understanding-v1/README.md`
- `datasets/corpora/rtl-understanding-v1/cases/single-clock-controller-clock-reset-extraction/record.json`
- `datasets/corpora/rtl-understanding-v1/cases/single-clock-controller-clock-reset-extraction/provenance.yaml`

## What The First Record Actually Means

The new dataset record is a machine-readable training/eval row.

Input:

- one RTL module

Task:

- extract clock and reset information

Gold output:

- one clock: `clk_i`
- one reset: `rst_n`
- reset edge: `negedge`
- active level: `low`
- style: `asynchronous`

Evidence:

- the `always_ff @(posedge clk_i or negedge rst_n)` line in the RTL

This is the correct kind of first record because it is:

- small
- real
- reviewable
- deterministic
- easy to expand later

## Validation Performed

I ran the repo's lightweight checks after the edits:

- `python3 scripts/repo_lint.py`
- `python3 scripts/check_structured_files.py`

Both passed.

This means:

- Markdown links were not broken by the doc changes
- the new JSON and YAML files are syntactically valid

## Current Repo State After This Session

The repo now has:

- a revised public dataset strategy
- a corrected plan filename
- an initial dataset schema area
- an initial corpus area
- one real canary record
- updated repo docs that acknowledge the new structure

What the repo does **not** have yet:

- dataset build scripts
- dataset validation scripts beyond syntax checks
- train/validation/test split files
- multiple records for the same task
- Hugging Face export automation

So this is the **correct beginning**, not the finished system.

## Recommended Next Steps

Recommended order:

1. Add 2-4 more `clock_reset_extraction` records from existing RTL fixtures.
2. Add split files for the canary corpus.
3. Add a small dataset validator script for schema and required fields.
4. Add one more deterministic `rtl-understanding` task such as `interface_extraction`.
5. Only after that, start `rtl-quality` mutation work.

## Final Summary

This session did not try to do too much.

That was intentional.

For dataset work, the dangerous mistake is to go directly to "collect lots of
data" before defining:

- what one record is
- how one task is scored
- how provenance is stored
- how CI and repo policy affect the data

What we did here was build the **foundation**:

- clean plan
- first schema
- first record
- first corpus location

For a real engineering dataset effort, that is the right first step.
