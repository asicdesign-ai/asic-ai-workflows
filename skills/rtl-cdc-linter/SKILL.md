---
name: rtl-cdc-linter
description: >
  Lint Verilog or SystemVerilog RTL for clock domain crossing (CDC) violations.
  Use this skill whenever the user asks to check for CDC issues, find unsynchronized
  crossings, review multi-clock designs, audit clock domain safety, or look for
  metastability risks in HDL code. Also trigger when the user pastes or points to
  an RTL module with multiple clocks and asks for a review, even if they don't
  explicitly say "CDC". This is a pre-EDA lint that catches issues early, before
  formal CDC tools like Spyglass or Meridian run.
---

# RTL CDC Linter Skill

Analyze Verilog/SystemVerilog RTL for clock domain crossing violations. Produce a
structured YAML report catching CDC issues early — before formal EDA tools run.

Scope: file-level (single module), small-to-mid scale. Not a replacement for
Spyglass or Meridian — think of it as a fast local lint pass.

## Rules

Apply these repo rules before analysis and output generation:

- `../../rules/common/evidence-grounding.md`
- `../../rules/common/output-discipline.md`
- `../../rules/cdc/classification.md`

## Analysis

Read the module and perform these steps in a single pass:

1. **Identify clock domains** — find every clock from `always_ff @(posedge ...)` blocks and edge expressions. Map each signal to its domain based on which clock drives it. Combinational signals inherit the domain of their inputs; mixed-domain combinational signals are crossing points.

2. **Detect crossings** — a crossing occurs when a signal from domain A is read in domain B. Check registered use (RHS of `always_ff`), combinational use (`always_comb`/`assign`), and port connections. Emit one crossing per unique `(signal, source_domain, dest_domain)` tuple and merge all destination-domain consume sites into its `line` field.

3. **Classify** — determine synchronization status, method, and severity using `../../rules/cdc/classification.md`.

4. **Suggest fixes** — for medium, high, and critical violations, name the smallest valid CDC structure and where it should live. For single-bit unsynchronized crossings, the default fix is a 2-FF synchronizer in the destination domain.

## Output Format

Produce a single YAML document:

```yaml
module: <module_name>
file: <file_path>
clock_domains:
  - name: <clock_signal_name>

crossings:
  - id: CDC-<NNN>
    signal: <signal_name>
    width: <bit_width>
    source_domain: <clock_name>
    dest_domain: <clock_name>
    line: <line_number or list of lines where signal is consumed>
    direction: "<source_clock> -> <dest_clock>"
    synchronized: <true | false>
    sync_method: <"2ff" | "3ff" | "gray" | "handshake" | "toggle_snapshot" | "async_fifo" | "pulse_sync" | "none">
    severity: <"critical" | "high" | "medium" | "low" | "info">
    description: <brief explanation>
    fix: <brief remediation, omit for info-level>

summary:
  total_crossings: <N>
  violations: <N>
  by_severity:
    critical: <N>
    high: <N>
    medium: <N>
    low: <N>
    info: <N>
```

**Conventions:**
- Number IDs sequentially: CDC-001, CDC-002, etc.
- `line` = where the signal is *consumed*, not produced. Use a list `[42, 79]` for multiple sites.
- Only list **violations** (severity > info) in the crossings array. Do not list properly synchronized crossings — they add output bulk without actionable value. The summary `by_severity.info` count is sufficient to show that safe crossings were analyzed.
- `clock_domains` lists domain names only — do not enumerate every signal per domain.

## Scope Limitations

- **Can do**: Single-module analysis, clock domain identification, synchronizer pattern recognition, unprotected crossing detection.
- **Cannot do**: Full IP hierarchy elaboration, generated clock analysis, SDC verification, or replace formal CDC tools.

## Not Covered

- Reset domain crossings
- Glitch-free clock muxing
- Power-domain crossings
