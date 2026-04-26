# Industry-Grade RTL Timing Analyzer Skill Plan

## Goal

Upgrade the existing `rtl-timing-path-analyzer` skill into an industry-grade
pre-synthesis RTL timing analyzer that designers can use before any synthesis or
STA run.

The skill should provide real-world timing feedback from RTL alone. It should
remain EDA-tool agnostic, work primarily on SystemVerilog and Verilog, and be
designed so other RTL-like or proprietary languages can be analyzed through a
language-neutral intermediate representation.

This plan follows the `skill-creator` guidance:

- keep the required `SKILL.md` concise and procedural
- move detailed reusable guidance into `references/`
- add deterministic scripts where repeated analysis should not be rewritten by
  the model
- validate the skill with schemas, fixtures, smoke cases, and forward tests

## Target Capability

The upgraded skill should answer these questions:

- what register-to-register paths are structurally deep
- what operations dominate each path
- which paths are likely timing risks before synthesis
- what RTL changes could reduce risk
- which conclusions are unsupported because source, hierarchy, constraints, or
  language semantics are missing

The skill should not claim:

- signoff timing
- real slack
- post-synthesis critical paths
- post-layout or clock-tree effects
- actual cell delays unless the user provides a calibrated timing model
- false-path or multicycle behavior without explicit user-provided constraints

## Naming Decision

The current repository skill is named:

- `skills/rtl-timing-path-analyzer/`

The user-facing name `rtl-timing-analyzer` is clearer for the upgraded scope.
There are two acceptable paths:

1. Keep the folder and slug as `rtl-timing-path-analyzer` to avoid repo-wide
   reference churn.
2. Rename to `rtl-timing-analyzer` and update all references in `README.md`,
   flows, eval metadata, schemas, validators, and smoke assets.

Recommended first step: keep the existing slug and update the description to make
the broader capability clear. Rename later only if the repository adopts a
formal naming cleanup.

## Current Repository Baseline

The existing timing skill already provides:

- a pre-synthesis timing-risk scope
- register discovery from explicit RTL evidence
- reg-to-reg fanin tracing
- configurable gate-depth estimates in
  `skills/rtl-timing-path-analyzer/default_config.yaml`
- ranked YAML output
- smoke cases for a simple hard path, a cross-module path, an unresolved
  FF-like macro, and a load-store command processor fixture

The main gaps are:

- no language-neutral IR
- no deterministic parser or analyzer scripts
- permissive schema validation
- limited path classes
- limited confidence and uncertainty modeling
- limited real-design timing patterns in the smoke suite
- no explicit adapter contract for proprietary or unknown languages
- no separation between raw depth, timing risk, and evidence confidence

## Architecture

Use a two-stage architecture:

1. Source adapter
2. Timing IR analyzer

The source adapter converts source artifacts into a normalized timing IR. The
analyzer consumes only that IR and emits the timing report.

This keeps the timing analysis language agnostic. SystemVerilog and Verilog get
a built-in adapter. Unknown or proprietary languages can be analyzed when the
user or a project-specific tool provides equivalent IR.

## Timing IR

Add a schema:

- `schemas/timing-ir.schema.json`

The IR should model:

- source files and language identifiers
- modules or design units
- ports, directions, widths, and source locations
- signals, widths, packed or unpacked shape where known
- sequential elements, clocks, resets, enables, and register evidence
- combinational assignment nodes
- operation nodes such as add, compare, mux, reduction, shift, multiply, concat,
  select, function call, and unknown operation
- hierarchy and instance port bindings
- unresolved modules, cells, macros, functions, and language constructs
- source locations for all evidence-backed objects

The IR should not require SystemVerilog-specific concepts. It should express the
semantic structures needed for timing:

- flip-flop or latch-like sequential storage
- combinational logic
- connectivity
- bit width
- hierarchy
- operation class
- endpoint relationship

## Language Adapter Contract

Add a reference:

- `skills/rtl-timing-path-analyzer/references/language-adapter-contract.md`

The adapter contract should define the minimum information needed to analyze any
language:

- how registers or sequential elements are proven
- how combinational assignments are represented
- how widths are determined or marked unknown
- how clock and reset evidence is recorded
- how instances and hierarchy are represented
- how unknown language constructs are surfaced as unresolved nodes
- how source locations are preserved

For proprietary or unknown languages, the skill should not pretend to understand
syntax. It should request either:

- a timing IR file following the schema
- a small adapter description that maps the language's sequential and
  combinational constructs into the IR
- manually extracted register, operation, and connectivity data

## Skill Structure

Keep `SKILL.md` concise and procedural.

Add references:

- `references/timing-analysis-model.md`
- `references/language-adapter-contract.md`
- `references/operation-depth-model.md`
- `references/optimization-guidance.md`

Recommended responsibility split:

- `SKILL.md`: trigger description, inputs, workflow, output contract, hard limits
- `timing-analysis-model.md`: path construction, endpoint classes, confidence
  rules, hierarchy handling
- `language-adapter-contract.md`: IR contract for SV/V and other languages
- `operation-depth-model.md`: configurable operation-depth formulas and
  calibration guidance
- `optimization-guidance.md`: RTL-level mitigation patterns and when they apply

## Deterministic Scripts

Add scripts under the skill:

- `skills/rtl-timing-path-analyzer/scripts/extract_sv_timing_ir.py`
- `skills/rtl-timing-path-analyzer/scripts/analyze_timing_ir.py`

The extractor should be conservative and best effort. It should prefer emitting
unresolved objects over inventing behavior.

The analyzer should:

- consume timing IR JSON or YAML
- build path graphs
- identify timing endpoints
- rank paths
- compute depth estimates from config
- compute risk and confidence
- emit a timing report matching `schemas/timing-report.schema.json`

This makes repeated timing analysis less dependent on free-form reasoning and
keeps complex graph traversal outside `SKILL.md`.

## Analysis Workflow

The upgraded skill should perform these steps:

1. Load source RTL files, filelists, or timing IR.
2. If source is SystemVerilog or Verilog, run the SV/V adapter where possible.
3. If source is another language, require a timing IR or adapter mapping before
   claiming analysis coverage.
4. Identify all sequential endpoints with explicit evidence.
5. Build combinational fanin and fanout graphs between endpoints.
6. Classify paths by endpoint type.
7. Estimate operation depth using the configured model.
8. Compute risk from depth, operation type, path structure, clock relationship,
   fanout hints, hierarchy uncertainty, and user-provided target context.
9. Compute confidence from evidence quality and unresolved content.
10. Emit ranked paths, bottlenecks, optimization candidates, unresolved items,
    assumptions, and summary counts.

## Path Classes

Report these path classes:

- `reg_to_reg`
- `input_to_reg`
- `reg_to_output`
- `input_to_output`
- `cross_clock_reg_to_reg`
- `unresolved`

The primary ranking should focus on `reg_to_reg` paths because those best match
pre-synthesis timing-closure risk. Boundary paths are still useful for block
integration and should be reported separately when visible.

Cross-clock reg-to-reg paths should not be treated as ordinary single-cycle
timing paths unless explicit clock relationship evidence is provided. They should
be surfaced as timing-unresolved or CDC-related risk, not as safe or closed.

## Configuration

Extend `default_config.yaml` with:

- `analysis_mode`: `balanced`, `conservative`, or `optimistic`
- `target_clock_period`: optional
- `target_units`: optional
- `depth_thresholds`
- `risk_thresholds`
- `confidence_thresholds`
- `gate_depth_model`
- `operation_weights`
- `uncertainty_penalties`
- `report`

Depth and risk should be separate. A path can have moderate depth but high risk
if it contains unresolved hierarchy, a multiply, a wide priority mux, or unknown
operation semantics.

The default model should remain unitless unless the user provides calibration.
If calibrated per-node or per-operation delay data is provided, the report may
include estimated delay, but it must label the estimate as calibrated input-based
and not signoff.

## Timing Risk Classification Rule

Keep:

- `rules/timing/register-evidence.md`

Add:

- `rules/timing/rtl-timing-risk-classification.md`

The new rule should define:

- risk levels: `critical`, `hard`, `moderate`, `easy`, `unresolved`
- confidence levels: `high`, `medium`, `low`
- how depth maps to risk
- how uncertainty changes risk and confidence
- what evidence is required for each path class
- when a path must remain unresolved
- prohibited claims about slack, signoff, synthesis optimization, and timing
  exceptions

## Timing Report Schema

Replace the permissive timing report schema with a strict contract.

The report should include:

- `module`
- `files`
- `config`
- `analysis_context`
- `assumptions`
- `registers`
- `paths`
- `bottlenecks`
- `optimization_candidates`
- `unresolved`
- `summary`

Each path should include:

- `id`
- `path_type`
- `from`
- `to`
- `clock_relationship`
- `depth`
- `risk`
- `confidence`
- `stages`
- `evidence`
- `crosses_module`
- `module_path`
- `description`
- `suggestion`
- `latency_impact`

Each stage should include:

- `op`
- `width`
- `depth`
- `source`
- `line`
- `confidence`

The schema should reject invalid enum values, missing evidence, malformed path
IDs, negative depths, and inconsistent summary counts.

## Optimization Guidance

Suggestions should be practical RTL feedback. Examples:

- insert a pipeline stage
- precompute compare results
- split arithmetic across cycles
- move a mux before expensive logic when it reduces width
- flatten or balance mux trees
- replace a priority chain with parallel decode when priority is not required
- use one-hot or gray encoding only when it matches design intent
- register memory read or write-control paths
- isolate multiply or wide arithmetic into a staged datapath

Each suggestion should state whether it changes latency. Designers need to know
whether a fix is local or architectural.

## Fixtures And Smoke Coverage

Expand timing fixtures to cover:

- simple adder reg-to-reg path
- chained adder path
- multiply-accumulate path
- compare plus mux path
- wide case mux
- priority if/else chain
- variable barrel shift
- reduction tree
- function-based combinational logic
- generate-loop combinational logic
- FSM next-state decode
- memory read path
- cross-module reg-to-reg path
- unresolved black-box submodule
- unresolved macro or library cell
- cross-clock register path
- input-to-reg boundary path
- reg-to-output boundary path
- timing IR for a proprietary or unknown language

Each smoke case should include:

- source or IR input
- expected timing report
- metadata assertions
- schema validation
- line-level evidence expectations

## Validators

Update:

- `scripts/report_validators.py`
- `scripts/check_eval_smoke.py`
- `schemas/timing-report.schema.json`

Validator checks should include:

- required top-level sections
- strict enum validation
- path ID format
- non-negative integer depth
- valid confidence and risk values
- valid endpoint type and path type
- stage depth sums matching path depth where applicable
- summary counts matching emitted paths
- unresolved objects carrying reason and source evidence
- no missing line evidence for evidence-backed source findings

## Flow Integration

Update:

- `flows/block-level-rtl-plan/FLOW.md`
- `skills/block-rtl-package-assembler/SKILL.md`

The block-level RTL plan should keep timing advisory unless the RTL structure
clearly forces a redesign. The handoff package should summarize:

- hard-or-worse path count
- deepest path depth
- unresolved timing object count
- lowest timing confidence
- highest timing risk
- whether any timing fix requires latency or interface changes

DV planning should import timing findings only as risk and prioritization
signals. It should not convert timing risk into unsupported functional
requirements.

## Forward Testing

Use the `skill-creator` forward-testing guidance after the first implementation.
Ask fresh agents to use the skill on raw fixtures without leaking the intended
answers.

Forward-test prompts should look like:

```text
Use the rtl-timing-path-analyzer skill at skills/rtl-timing-path-analyzer to
analyze these RTL files and emit the timing report.
```

The validation should inspect:

- whether the skill asks for IR when the language is unknown
- whether unresolved hierarchy stays unresolved
- whether reg-to-reg paths are ranked correctly
- whether suggestions are useful and do not invent synthesis behavior
- whether output conforms to the schema on the first attempt

## Rollout Order

1. Add timing IR schema and language adapter contract.
2. Tighten the timing report schema while preserving compatibility where needed.
3. Add the timing risk classification rule.
4. Refactor `SKILL.md` and add references.
5. Extend `default_config.yaml`.
6. Add deterministic IR analyzer script.
7. Add SV/V extraction script or staged extractor scaffolding.
8. Expand fixtures and smoke expected outputs.
9. Strengthen validators.
10. Update flow and handoff package summaries.
11. Run repo checks and smoke validation.
12. Forward-test the skill on fresh tasks and iterate.

## Acceptance Criteria

The upgraded skill is ready when it can:

- analyze SystemVerilog and Verilog RTL without vendor EDA tools
- consume timing IR for other or proprietary languages
- emit deterministic YAML matching a strict schema
- rank register-to-register paths by structural timing risk
- explain every path with source-level evidence
- distinguish raw depth, risk, and confidence
- handle missing hierarchy conservatively
- avoid unsupported slack or signoff claims
- provide RTL-level suggestions that designers can act on before synthesis
- pass expanded smoke evals and repository validation scripts

## Residual Limits

Even after this upgrade, the skill remains a pre-synthesis estimator. It cannot
replace synthesis, STA, SDC analysis, gate-level netlist review, clock-tree
analysis, placement, routing, or signoff timing closure.
