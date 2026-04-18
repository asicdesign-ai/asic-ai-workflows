# Full RTL Dataset Plan

## Objective

Build a deterministic, publishable dataset pipeline for front-end RTL tasks and
use Hugging Face as the distribution layer.

The repository remains the source of truth for:

- schemas
- canonical cases
- provenance
- validation rules
- export scripts

## V1 Scope

V1 should stay narrow and realistic:

- block-level and leaf-module RTL only
- Verilog/SystemVerilog only
- small single-file modules first
- small multi-file compile units second
- tasks that can be scored deterministically

V1 is not the place for:

- full-chip datasets
- signoff timing claims
- place-and-route or GDS data
- waveform-heavy simulation datasets
- private RTL without explicit publication rights

## Design Principles

- Tasks, not file dumps
- Structured labels, not vague prose
- Deterministic scoring where possible
- Explicit provenance for every case
- Split hygiene by lineage, not random row shuffling
- Hugging Face as a release target, not the authoring surface

## V1 Dataset Families

### Dataset A: `rtl-understanding`

Purpose:
Create a clean structural-understanding dataset for small RTL blocks.

Recommended V1 tasks:

- `interface_extraction`
- `clock_reset_extraction`
- `state_element_inventory`

Stretch task after V1 stabilization:

- `module_summary`

Rationale:
The extraction tasks are easier to score deterministically and fit the repo's
evidence-grounded style better than free-form summaries.

Representative record shape:

```json
{
  "record_id": "rtl-understanding-000001",
  "schema_version": "1.0.0",
  "task": "clock_reset_extraction",
  "input": {
    "language": "systemverilog",
    "top_module": "event_counter",
    "rtl_text": "module event_counter ...",
    "compile_unit": {
      "files": ["rtl/event_counter.sv"],
      "filelist": null
    }
  },
  "target": {
    "clocks": [
      {
        "name": "clk",
        "edge": "posedge"
      }
    ],
    "resets": [
      {
        "name": "rst_n",
        "active_level": "low",
        "style": "asynchronous"
      }
    ]
  },
  "metadata": {
    "source_type": "synthetic",
    "source_group": "counter_family_a",
    "difficulty": "easy",
    "domain_tags": ["counter"]
  },
  "provenance": {
    "license": "MIT",
    "generator": "scripts/build_rtl_dataset.py",
    "mutation_id": null
  }
}
```

### Dataset B: `rtl-quality`

Purpose:
Create a structured quality dataset for front-end RTL review, lint-style issue
classification, and future repair workflows.

Recommended V1 task:

- `quality_classification`

Stretch tasks after V1 stabilization:

- `issue_localization`
- `candidate_fix`

Recommended issue taxonomy for the first release:

- `latch_inference`
- `procedural_assignment_misuse`
- `width_mismatch`
- `reset_inconsistency`
- `multiple_driver_risk`

Important constraint:
Do not reduce the target to a binary `good` or `bad` label. The record should
carry issue class, severity, and evidence.

Representative record shape:

```json
{
  "record_id": "rtl-quality-000001",
  "schema_version": "1.0.0",
  "task": "quality_classification",
  "input": {
    "language": "systemverilog",
    "top_module": "event_counter",
    "rtl_text": "module event_counter ..."
  },
  "target": {
    "overall_label": "bad",
    "compile_expectation": "compile_clean",
    "issues": [
      {
        "category": "latch_inference",
        "severity": "high",
        "message": "Combinational process leaves a driven signal unassigned on some paths.",
        "evidence": [
          {
            "file": "inline",
            "line_start": 18,
            "line_end": 27
          }
        ]
      }
    ]
  },
  "metadata": {
    "source_type": "mutation",
    "source_group": "counter_family_a",
    "difficulty": "easy"
  },
  "provenance": {
    "license": "MIT",
    "generator": "scripts/mutate_rtl.py",
    "mutation_id": "remove_default_assignment_v1"
  }
}
```

## Source Strategy

Use a staged source hierarchy.

### Tier 0: Repo-Native Canonical Cases

Start with small modules authored inside this repository or added explicitly for
dataset use.

Benefits:

- clean licensing
- stable review expectations
- easy mutation and relabeling
- full control over filelist and compile behavior

### Tier 1: Synthetic Families

Generate small blocks with controlled variation:

- counters
- FIFOs
- FSM controllers
- arbiters
- register banks

Synthetic data is acceptable for V1 if it is structured, validated, and
lineage-tracked.

### Tier 2: Public Open-Source RTL

Add public modules only when each borrowed case carries explicit provenance:

- upstream repository URL
- exact commit SHA
- module path
- license
- project-level evidence
- exact-module evidence when available

Do not publish public-source records with unclear provenance or uncertain reuse
rights.

## Provenance Contract

Every case should carry machine-readable provenance, ideally in a per-case
`provenance.yaml` or equivalent record field.

Minimum provenance fields:

- `source_type`
- `source_group`
- `top_module`
- `origin_repo`
- `origin_commit`
- `origin_path`
- `license`
- `generator`
- `generator_version`
- `mutation_id`
- `human_review_status`

This is required for reproducibility, licensing, and split hygiene.

## Generation Pipeline

1. Create or ingest one canonical good compile unit.
2. Normalize compile-unit metadata:
   - identify `top_module`
   - capture source files
   - capture `.f` filelist when needed
3. Run structural validation:
   - Verilator compile for units expected to compile
   - `slang` frontend check for the same units
4. Extract metadata:
   - clock count
   - reset count
   - module family
   - size and difficulty features
5. Create understanding records.
6. Apply controlled mutations for quality records.
7. Attach issue labels, severity, and evidence.
8. Deduplicate by normalized text and lineage.
9. Assign train/validation/test splits by source group.
10. Export immutable release artifacts.

## Mutation Policy

The mutation engine is critical, but it must stay realistic.

Recommended mutation rules:

- preserve syntax validity unless a task explicitly targets compile errors
- prefer bugs that designers and lint tools really see in front-end review
- keep a one-to-one link from mutated record back to canonical source
- record the exact mutation rule used

Examples:

- remove default assignment from a combinational block
- replace non-blocking assignment with blocking assignment in sequential logic
- alter declared signal width or slice width
- drop or mismatch a reset path
- add a second procedural driver

Important repo constraint:
GitHub CI compiles every checked-in `.sv` and `.v` file. Any intentionally bad
RTL that may fail compile should live inside dataset records as text, or under a
non-compiled artifact format, rather than as repo-visible `.sv` files.

## Split Strategy

Never split these datasets by random record-level shuffling.

Split by lineage:

- canonical source module
- mutation family
- upstream project or family
- synthetic template family

Rules:

- no source module should appear in more than one split
- sibling mutations should stay in one split
- near-duplicates should stay in one split
- the test split should include unseen families, not just unseen record IDs

## Validation Gates

Each release candidate should pass:

- schema validation
- required-field validation
- provenance completeness check
- license completeness check
- split leakage check
- duplicate and near-duplicate check
- compile validation for records marked `compile_clean`
- filelist validation for multi-file compile units
- label consistency check
- class-balance sanity check
- sample human audit

## Recommended Repository Layout

Use the repository as the factory and publish derived snapshots outward.

```text
datasets/
  fixtures/
  corpora/
    rtl-understanding-v1/
      cases/
        rtl-understanding-000001/
          record.json
          provenance.yaml
      splits/
        train.txt
        validation.txt
        test.txt
    rtl-quality-v1/
      cases/
        rtl-quality-000001/
          record.json
          provenance.yaml
      splits/
        train.txt
        validation.txt
        test.txt

schemas/
  dataset/
    rtl-record-common.schema.json
    rtl-understanding.schema.json
    rtl-quality.schema.json

scripts/
  build_rtl_dataset.py
  mutate_rtl.py
  validate_rtl_dataset.py
  check_dataset_splits.py
  export_hf_dataset.py
```

This keeps `datasets/fixtures/` for current smoke-style repo assets while giving
the future corpus work its own deterministic home.

## Hugging Face Release Contract

Publish stable dataset repositories and version them with releases rather than
baking size labels into the repository name.

Recommended Hugging Face repositories:

- `asicdesign-ai/rtl-understanding`
- `asicdesign-ai/rtl-quality`

Recommended release tags:

- `v0.1.0`
- `v0.2.0`

Each release should include:

- exported `train`, `validation`, and `test` splits
- schema reference
- dataset card
- license summary
- provenance summary
- known limitations and bias notes

## Milestones

### Milestone 0: Contract Definition

Deliverables:

- per-record schema
- provenance template
- issue taxonomy
- split policy

Exit criteria:

- record format is stable enough to build scripts against
- provenance and licensing fields are agreed

### Milestone 1: Canary Dataset

Deliverables:

- 25 `rtl-understanding` cases
- 25 `rtl-quality` cases
- basic build and validation scripts

Exit criteria:

- end-to-end local build works
- compile expectations are correct
- split leakage checks pass

### Milestone 2: First Public Release

Deliverables:

- 100 `rtl-understanding` cases
- 100 `rtl-quality` cases
- Hugging Face export
- dataset cards

Exit criteria:

- all validation gates pass
- provenance is complete for every published record
- the release is small but benchmark-usable

## Expansion After V1

Only expand after the first release is clean and repeatable.

Next candidates:

- `issue_localization`
- `candidate_fix`
- spec-to-RTL alignment
- CDC and RDC classification corpora
- timing-structure and path-risk corpora
- carefully screened public-source modules

Do not expand into physical-design or signoff datasets until the front-end RTL
pipeline is already stable.
