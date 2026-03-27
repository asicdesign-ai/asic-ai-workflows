---
name: cdc-analysis
description: >
  Analyze Verilog or SystemVerilog RTL for clock domain crossing (CDC) violations.
  Use this skill whenever the user asks to check for CDC issues, find unsynchronized
  crossings, review multi-clock designs, audit clock domain safety, or look for
  metastability risks in HDL code. Also trigger when the user pastes or points to
  an RTL module with multiple clocks and asks for a review, even if they don't
  explicitly say "CDC". This is a pre-EDA lint — it catches issues early, before
  formal CDC tools like Spyglass or Meridian run.
---

# CDC Analysis Skill

Analyze Verilog/SystemVerilog RTL modules for clock domain crossing violations and
produce a structured YAML report. The goal is to catch CDC issues early — before
formal EDA tools run — so engineers get fast feedback during development.

This is a small-to-mid scope analysis tool. It works at file scope (single module)
and can reason about cross-module crossings when multiple files are provided. It is
not meant to replace full-chip CDC tools like Spyglass or Meridian — think of it as
a fast, local lint pass.

## Analysis Methodology

Work through the RTL systematically in these phases. Each phase builds on the
previous one's results.

### Phase 1: Identify Clock Domains

Parse the module to find every distinct clock. Clocks appear in:
- `always_ff @(posedge clk_x ...)` or `always @(posedge clk_x ...)`
- Module port declarations (inputs named `clk*`, `clock*`, or used in edge expressions)
- Generated clocks (dividers, gated clocks)

For each clock, build a **domain membership map**: which signals (registers and wires)
belong to which domain. A signal belongs to a domain if:
- It is assigned inside an `always_ff` / `always` block clocked by that clock
- It is a combinational function (`assign`, `always_comb`) whose inputs all belong
  to one domain — the output inherits that domain
- It is a module input annotated with a comment indicating its domain

If a combinational signal's inputs span multiple domains, that signal is itself a
CDC crossing point (and likely a violation).

### Phase 2: Detect Crossings

A **crossing** occurs when a signal from domain A is read (used) in a context
belonging to domain B. Scan for:

1. **Registered crossings** — signal from domain A appears on the RHS of an
   `always_ff` block clocked by domain B
2. **Combinational crossings** — signal from domain A feeds into `always_comb`
   or `assign` logic whose output is consumed by domain B
3. **Port crossings** — in a submodule instantiation, a signal from domain A
   connects to a port that is used in domain B inside the submodule

For each crossing, record the source signal, source domain, destination domain,
and the line number(s) where it occurs.

### Phase 3: Classify Each Crossing

For every crossing found, determine if it is properly synchronized. A crossing
is **safe** if the signal passes through a recognized synchronization structure
before being used. Common synchronizer patterns:

| Pattern | How to Recognize | Safe For |
|---------|-----------------|----------|
| **2-FF synchronizer** | Two back-to-back FFs in destination domain, first FF's D input is the cross-domain signal, second FF's D input is the first FF's Q. Often named `*_m1`/`*_sync` or `*_d1`/`*_d2`. | Single-bit signals |
| **3-FF synchronizer** | Same as 2-FF but with three stages. | Single-bit, higher MTBF |
| **Gray-code + sync** | Multi-bit bus encoded in Gray before crossing, then synced and decoded. | Multi-bit counters/pointers |
| **Handshake / req-ack** | A request signal crosses one way, an acknowledge crosses back, both through synchronizers. Data is held stable between req and ack. | Multi-bit data with handshake |
| **Toggle + snapshot** | Source toggles a flag and holds data stable; destination syncs the toggle and samples on edge detect. | Multi-bit status/snapshot |
| **FIFO with dual-clock pointers** | Async FIFO where write and read pointers cross domains via Gray-coded synchronizers. | Stream data |
| **Pulse synchronizer** | Single-bit pulse converted to toggle, synced, then edge-detected back to pulse in destination domain. | Single-cycle events |

A crossing is a **violation** if none of these patterns are present — the raw
signal from domain A is used directly in domain B.

### Phase 4: Assess Severity

Each violation gets a severity based on the practical risk:

| Severity | Criteria |
|----------|----------|
| **critical** | Multi-bit signal crossing without any synchronization — can cause data corruption, not just metastability. Includes multi-bit bus, enum/FSM state, or counter sampled directly in another domain. |
| **high** | Single-bit signal crossing without synchronization — metastability risk that can propagate. Includes control signals like valid, ready, enable. |
| **medium** | Signal is partially synchronized (e.g., only 1 FF stage) or synchronizer structure exists but has a subtle flaw (e.g., combinational logic between sync stages). |
| **low** | Crossing exists but is in a quasi-static path (configuration register written once at init), or there is a plausible synchronization structure that could not be fully confirmed. |
| **info** | Crossing detected but appears properly synchronized. Reported for completeness so the engineer can verify. |

### Phase 5: Suggest Fixes

For each violation (severity medium or above), provide a concrete fix suggestion:
- Which synchronizer pattern to use and why
- Where to place it (which domain's `always_ff` block)
- If a multi-bit signal, whether to use Gray coding, a handshake, a snapshot, or an async FIFO

Keep suggestions practical — prefer the simplest synchronizer that solves the problem.

## Output Format

Produce a single YAML document. Use this structure exactly:

```yaml
module: <module_name>
file: <file_path>
clock_domains:
  - name: <clock_signal_name>
    signals:
      - <signal_1>
      - <signal_2>

crossings:
  - id: CDC-<NNN>
    signal: <signal_name>
    width: <bit_width>
    source_domain: <clock_name>
    dest_domain: <clock_name>
    line: <line_number or range>
    direction: "<source_clock> -> <dest_clock>"
    synchronized: <true | false>
    sync_method: <"2ff" | "3ff" | "gray" | "handshake" | "toggle_snapshot" | "async_fifo" | "pulse_sync" | "none">
    severity: <"critical" | "high" | "medium" | "low" | "info">
    description: <one-line explanation of what is crossing and why it matters>
    fix: <suggested remediation, omit for info-level>

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
- Number crossing IDs sequentially: CDC-001, CDC-002, etc.
- `line` should be the line where the cross-domain signal is *consumed* (read),
  not where it is produced
- List every crossing — including safe ones (as `info`) — so the report is a
  complete map of all domain boundaries
- Keep `description` to one sentence
- Keep `fix` to 1–2 sentences; reference the synchronizer pattern by name

## Scope Limitations

Be transparent about what this analysis can and cannot do:

- **Can do**: Single-module analysis, identify clock domains from `always_ff` blocks,
  recognize common synchronizer patterns, flag unprotected crossings
- **Cannot do**: Full elaboration across an IP hierarchy, analyze generated clocks
  with complex gating, verify timing constraints (SDC), or replace formal CDC tools
- **When unsure**: If a signal's domain is ambiguous (e.g., clock comes from a
  parameterized mux, or a signal is conditionally driven from different domains),
  flag it as `severity: low` with a note explaining the ambiguity rather than
  silently ignoring it

## What This Skill Does NOT Cover

- Reset domain crossings (related but different topic)
- Glitch-free clock muxing analysis
- Power-domain crossings
