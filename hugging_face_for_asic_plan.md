# Hugging Face for ASIC Plan

## Purpose

Define how `asic-ai-workflows` should approach public Hugging Face publication
for ASIC and RTL data without weakening the repository's source-of-truth,
provenance, or engineering discipline.

## Recommended Position

The right first move is not to publish a generic "ASIC dataset" or a raw dump of
Verilog files.

The stronger position is to publish small, structured, task-specific datasets
for front-end RTL work with:

- explicit schemas
- deterministic targets
- compile-unit metadata
- provenance and licensing
- benchmark-friendly evaluation paths

Hugging Face should be the distribution channel.

`asic-ai-workflows` should remain the dataset factory and source of truth.

## Recommended V1 Scope

Keep the first public release narrow:

- front-end RTL only
- block or leaf-module scale
- Verilog/SystemVerilog only
- tasks that can be scored deterministically
- public or clearly licensable sources only

Do not start with:

- physical design or signoff data
- raw open-source RTL dumps
- unlabeled corpora
- private designs with unclear publication rights
- free-form tasks with weak scoring

## Highest-Value First Releases

### 1. `rtl-understanding`

Start with extraction tasks rather than open-ended summaries.

Recommended V1 tasks:

- `interface_extraction`
- `clock_reset_extraction`
- `state_element_inventory`

Add `module_summary` only after the extraction labels are stable and the scoring
rule is clear.

### 2. `rtl-quality`

Start with structured quality labeling rather than a shallow binary
"good vs bad" label.

Recommended V1 targets:

- overall quality label
- issue taxonomy
- severity
- evidence locations
- compile expectation

This is more useful for training and evaluation than a single `good` or `bad`
field with no evidence trail.

## Required Acceptance Gates

Every publishable record should have:

- stable `record_id`
- explicit `schema_version`
- exact source and provenance metadata
- clear license information
- `top_module` and compile-unit context
- deterministic gold target
- declared evaluation path
- split-group metadata to prevent train/test leakage

Additional repo-specific gates:

- compile-clean gold RTL must obey the existing Verilator and `slang` policy
- intentionally bad RTL that may fail compile should stay inside dataset records
  as text, not as checked-in `.sv` files that CI will compile
- multi-file examples must carry a `.f` manifest or equivalent compile-unit
  metadata

## Strategic Sequence

1. Define the per-record schema and provenance contract.
2. Build a small set of canonical repo-native cases.
3. Add generator and mutation scripts with lineage capture.
4. Validate labels, splits, and compile behavior locally.
5. Export immutable snapshots and publish them to Hugging Face with a dataset
   card.

## Success Criteria

The first release is successful if it is:

- small
- clean
- reproducible
- licensed correctly
- easy to benchmark
- obviously useful to front-end RTL engineers
