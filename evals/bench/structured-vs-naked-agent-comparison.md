# Structured vs Naked Agent Comparison Plan

## Objective

Compare AI agent performance on RTL design and lint-audit tasks when the agent
uses this repository's skills, rules, schemas, and optional `pyslang-mcp`
evidence against a baseline "naked" AI agent that receives the same user task
but no repo skill/rule context and no MCP access.

The comparison should measure engineering usefulness, not presentation quality.
Primary outcomes are correctness, reproducibility, evidence grounding,
schema compliance, compile health, and safe handling of uncertainty.

## Agent Configurations

Evaluate at least these arms:

| Arm | Skill/rule context | Output schemas | MCP access | Purpose |
| --- | --- | --- | --- | --- |
| Naked | None | None unless requested in prompt | None | Baseline free-form agent behavior |
| Structured | `rtl-designer`, `rtl-lint-auditor`, shared rules | Required | None | Measures skill/rule/schema value |
| Structured + MCP | Same as structured | Required | Read-only `pyslang-mcp` | Measures semantic tool evidence value |

Keep model, temperature, context window, timeout, retry policy, and token budget
identical across arms. Randomize task order and run at least three trials per
task to estimate variance.

## Benchmark Task Classes

### RTL Generation

Input: approved microarchitecture specifications or structured block
requirements.

Expected output: RTL design YAML compatible with
`schemas/rtl-design.schema.json`, including synthesizable SystemVerilog source
records, module descriptions, requirement traceability, unresolved items, and
`tool_evidence`.

Representative cases:

- Simple single-clock controller
- Counter or timer with threshold interrupt behavior
- Command FSM with explicit state transitions
- Block with underspecified reset policy
- Block with package or interface dependency
- Multi-file design requiring a filelist
- Parameterized width or depth behavior

### RTL Lint Audit

Input: existing RTL source text, optional filelist, and optional project root.

Expected output: RTL lint report YAML compatible with
`schemas/rtl-lint-report.schema.json`, including grounded findings, deterministic
severity, blocking flags, recommendations, and `tool_evidence`.

Representative cases:

- Clean single-clock RTL
- Inferred latch due to incomplete combinational assignment
- Width truncation on architecturally visible signal
- Reset style or polarity mismatch
- Multiple drivers
- Misleading `_sync` or `gray` naming without structural proof
- Parameterized width requiring semantic elaboration
- Multi-file package/import dependency

### Repair After Diagnostics

Input: generated RTL materialized to disk plus diagnostics from Verilator,
slang, or `pyslang-mcp`.

Expected output: revised RTL or a structured fix plan that preserves the original
requirements and explains any unresolved limitations.

Representative cases:

- Missing package import
- Port width mismatch
- Undefined module or interface reference
- Syntax error in generated source
- Parser-clean RTL that still contains a text-grounded lint hazard

## Ground Truth

Keep ground truth separate from prompts.

For RTL generation, do not require byte-for-byte golden RTL. Use executable and
reviewable properties:

- Schema-valid structured output
- Verilator compile success
- slang or `pyslang-mcp` parse success
- Synthesizable constructs only
- Requirement traceability completeness
- Explicit clock and reset behavior
- No invented interfaces, modules, packages, or protocol semantics
- Correct unresolved items for missing specification details

For lint audit, use curated expected findings:

- Expected finding category
- Required evidence file and line
- Accepted severity band
- Blocking expectation
- Accepted minimal fix recommendation
- Known false-positive traps
- Known parser-clean but lint-unsafe cases

## Metrics

### Machine-Checkable Metrics

- Output schema validity
- Required section completeness
- Allowed enum and ID format compliance
- Verilator compile pass or fail
- slang or `pyslang-mcp` parse diagnostics
- Count of generated RTL files and modules
- Count of unresolved items
- Count of invented objects
- Presence and validity of `tool_evidence`
- Latency, token usage, and retry count

### Lint Metrics

- True positives
- False positives
- False negatives
- Severity accuracy
- Blocking-flag accuracy
- File/line evidence accuracy
- Recommendation usefulness
- Correct normalization of external tool severity

### Human Review Metrics

Use blinded review. Reviewers should not know which arm produced an output.

Score each artifact from 0 to 3:

| Score | Meaning |
| --- | --- |
| 0 | Wrong, unsafe, or unusable |
| 1 | Partially useful but requires substantial correction |
| 2 | Mostly correct but incomplete or rough |
| 3 | Production-useful for this repository's stated scope |

Review dimensions:

- Engineering correctness
- Evidence grounding
- Requirement traceability
- Reset and clock clarity
- Minimality of design structure
- Severity consistency
- Uncertainty handling
- Avoidance of signoff overclaims

## MCP-Specific Evaluation

Measure `structured` against `structured + MCP` separately so MCP value is not
confused with skill/rule value.

MCP evidence should help most on:

- Filelist and include resolution
- Package, interface, and typedef discovery
- Design-unit inventory
- Hierarchy inspection
- Symbol declaration and reference lookup
- Parse and semantic diagnostics after generated RTL is materialized

MCP evidence should not be credited for:

- Claims of lint cleanliness from zero parser diagnostics alone
- CDC, timing, synthesis, simulation, or signoff claims
- Cases where no project root, filelist, source files, or materialized generated
  RTL exist

For `pyslang-mcp`, expected useful calls include:

- `pyslang_parse_filelist` or `pyslang_parse_files`
- `pyslang_get_project_summary`
- `pyslang_get_diagnostics`
- `pyslang_list_design_units`
- `pyslang_describe_design_unit`
- `pyslang_get_hierarchy`
- `pyslang_find_symbol`

## Procedure

1. Freeze the repository commit SHA, model version, prompt templates, and MCP
   server version.
2. Build the benchmark cases and store inputs separately from expected answers.
3. Run each task against each agent arm with identical execution settings.
4. Materialize generated RTL files before running compiler or MCP diagnostics.
5. Validate structured outputs with the repo validators.
6. Run Verilator, slang, and `pyslang-mcp` checks where applicable.
7. Compare lint findings against curated expected findings.
8. Send anonymized artifacts to reviewers for blind scoring.
9. Aggregate results by task class and by failure mode.
10. Preserve all prompts, outputs, tool transcripts, diagnostics, and reviewer
    notes.

## Success Criteria

The structured arms should materially improve:

- Schema validity
- Deterministic report shape
- Compile or parse success
- Requirement traceability
- Evidence-grounded findings
- Correct severity and blocking classification
- Explicit unresolved handling
- Avoidance of invented structure
- Avoidance of unsupported signoff claims

The MCP arm should additionally improve:

- Multi-file project understanding
- Package/interface/type discovery
- Diagnostics-grounded repair quality
- File/line and symbol evidence quality

The MCP arm should not increase unsafe overclaims or hide tool limitations.

## Reporting

Publish a scorecard with:

- Pass rate by arm and task class
- Schema validity rate
- Compile and parse success rate
- Lint precision, recall, and severity accuracy
- Average human review score
- Hallucination and unsafe-overclaim count
- Median latency and token usage
- Retry count
- Representative failures and root causes

Do not report only aggregate scores. Include failure-mode breakdowns so the
benchmark identifies which repo artifacts need improvement.

## Reproducibility Artifacts

Preserve:

- Benchmark input files
- Prompt templates
- Skill and rule versions
- Model and sampling settings
- MCP server version and tool schemas
- MCP transcript summaries
- Generated YAML reports
- Materialized RTL
- Verilator, slang, and `pyslang-mcp` logs
- Curated ground-truth findings
- Reviewer rubrics and anonymized scores
- Exact repository commit SHA

## CI Strategy

Keep live model comparisons out of normal PR CI because model output is variable
and can be expensive. Add a small deterministic smoke subset under
`evals/smoke/` only when outputs are stable and schema-backed.

Use an offline benchmark runner for full comparisons under `evals/bench/` or a
dedicated benchmark harness. The runner should produce immutable result bundles
that can be reviewed independently.
