---
name: sta-analysis
description: >
  Estimate combinational logic depth on register-to-register paths in Verilog or
  SystemVerilog RTL. Use this skill whenever the user asks to find timing-critical
  paths, estimate logic depth, check for deep combinational chains, review RTL for
  timing closure risk, or wants a pre-synthesis timing analysis. Also trigger when
  the user points to an RTL module and asks "will this meet timing?" or "what are
  the critical paths?", even without saying "STA". This is a pre-synthesis estimate —
  it helps engineers prioritize paths before running DC/Genus.
---

# Pre-Synthesis STA Skill

Estimate gate-level combinational depth on every register-to-register path in
Verilog/SystemVerilog RTL. Produce a ranked YAML report of timing paths ordered by
difficulty — the deepest paths are most likely to fail timing closure.

Scope: module-level first, cross-module when submodules are provided. Not a
replacement for PrimeTime or Tempus — think of it as a fast lint that flags
structurally deep paths before synthesis.

## Configuration

The user may provide an optional config YAML to override defaults. If none is
provided, use the defaults in `references/default_config.yaml`. The config controls:

- **`depth_thresholds`** — gate-level cutoffs for difficulty categories:
  - `critical`: ≥ 20 (default)
  - `hard`: ≥ 10
  - `moderate`: ≥ 5
  - below moderate = `easy`

- **`gate_depth_model`** — estimated gate levels per operation type. Defaults assume synthesis-realistic structures (CLA adders, Wallace tree multipliers):
  - 2:1 mux / ternary: **2** (AND-OR)
  - 4:1 mux: **4** (two stages of 2:1)
  - N:1 mux / case with N cases: **2 * ceil(log2(N))**
  - Comparator (==, !=): **1 + ceil(log2(W))** (XOR per bit + AND tree)
  - Comparator (<, >): **4 + 2 * ceil(log2(W))** (same as adder — subtract + check sign)
  - Adder/subtractor: **4 + 2 * ceil(log2(W))** (CLA/prefix tree — e.g. 32-bit ≈ 14 levels)
  - Incrementer (+1): **2 * ceil(log2(W))**
  - AND/OR/XOR reduction: **ceil(log2(W))**
  - Barrel shift (variable): **2 * ceil(log2(W))**
  - Multiply: **ceil(log2(W)) + 4 + 2 * ceil(log2(W))** (Wallace/Dadda CSA tree + final CPA — e.g. 32-bit ≈ 23 levels)
  - Constant shift, concat, bit-select: **0** (wiring)
  - Priority if-else chain: **2 * N** (N branches, chained muxes)

  The default model assumes synthesis will use optimized structures, which is
  what real tools (DC, Genus) produce. For worst-case ripple-carry estimates,
  the config file includes commented-out ripple variants that users can enable.

- **`report`** — output controls:
  - `max_paths`: cap output (0 = all, default)
  - `include_easy`: whether to list easy paths (default: false)
  - `sort_by`: `"depth"` descending (default)

Read `references/default_config.yaml` for the full schema with all defaults.

## Analysis

Read the module and perform these steps:

1. **Identify all registers** — registers can appear in multiple forms. Check all of these:

   - **`always_ff` / `always @(posedge ...)`** blocks — LHS signals are registers.
   - **Macro instantiations** — macros whose names contain `FF`, `DFF`, `MSFF`, `FLOP`, `REG`, or `LATCH` likely create registers. If the `` `define`` is in scope (same file or `` `include``d file), expand it to confirm. If not found, infer from the name: first argument is typically Q (output), second is D (input).
   - **Library cell instantiations** — cells named `*DFF*`, `*SDFF*`, `*MSFF*`, `*FD*`, `*SDFFRX*`, etc. Port `.Q` is output, `.D` is input, `.CK`/`.CLK` is clock.
   - **Module instantiations with FF-like names** — module names containing `flop`, `ff`, `reg`, `dff` — treat as register wrappers.

   For each register, record: signal name, width, clock, and the line where it's assigned.

   If a macro or cell can't be resolved and the name doesn't match known patterns, flag it as `unresolved` in the report rather than silently ignoring it.

2. **Trace combinational fanin for each register** — starting from the D-input of each destination register, walk backwards through combinational logic until hitting:
   - Another register's Q-output (→ this is the start of a reg-to-reg path)
   - A module input port (→ input-to-reg path)
   - A constant (→ terminates the path)

   For cross-module paths: if the fanin traces into a submodule port, follow the connection into the submodule's logic and continue tracing. Record the module hierarchy traversed.

3. **Estimate depth for each path** — sum the gate-level depth contributions of each operation along the path, using the `gate_depth_model` from config. For each operation, record what it is, its width, and its depth contribution.

4. **Categorize** — apply `depth_thresholds` from config to assign difficulty.

5. **Suggest optimizations** for `critical` and `hard` paths:
   - Pipeline insertion (add a register stage to break the path)
   - Restructure mux trees (e.g., move a wide mux before narrow logic)
   - Pre-compute comparisons in a prior cycle
   - Use a different encoding (one-hot vs binary for case statements)
   Keep suggestions to 1-2 sentences.

## Output Format

Produce a single YAML document:

```yaml
module: <module_name>
file: <file_path>
config: <"default" or path to user config>

registers:
  - name: <register_name>
    width: <bits>
    clock: <clock_name>
    source: <"always_ff" | "macro" | "library_cell" | "inferred">
    line: <line_number>

paths:
  - id: PATH-<NNN>
    from: <source_register or "INPUT:port_name">
    to: <dest_register>
    depth: <estimated_gate_levels>
    difficulty: <"critical" | "hard" | "moderate" | "easy">
    stages:
      - op: <operation_type>
        width: <bit_width>
        depth: <gate_levels_contributed>
        line: <line_number>
    crosses_module: <true | false>
    module_path: ["top", "sub1"]   # only if crosses_module
    description: <one-line path summary>
    suggestion: <optimization hint, only for critical/hard>

unresolved:
  - name: <macro_or_cell_name>
    line: <line_number>
    reason: <"macro definition not found" | "unknown cell library">

summary:
  total_registers: <N>
  total_paths: <N>
  by_difficulty:
    critical: <N>
    hard: <N>
    moderate: <N>
    easy: <N>
  deepest_path:
    id: <PATH-ID>
    depth: <N>
    from: <reg>
    to: <reg>
```

**Conventions:**
- Number path IDs sequentially: PATH-001, PATH-002, etc.
- Sort paths by depth descending (deepest first).
- Only list paths with difficulty above `easy` unless config says `include_easy: true`.
- `registers` section lists all identified registers with their detection method.
- `unresolved` section lists any macros or cells that couldn't be confirmed as registers or combinational.
- Keep `description` to one sentence. Keep `suggestion` to 1-2 sentences.

## Scope Limitations

- **Can do**: Single-module path tracing, cross-module tracing when all files are provided, macro expansion, library cell inference, configurable depth model.
- **Cannot do**: Actual gate-level netlist analysis, account for synthesis optimizations (retiming, logic restructuring), analyze clock tree depth, replace PrimeTime/Tempus.
- **When unsure**: Report the path with a note explaining the uncertainty (e.g., "depth estimate assumes ripple carry; synthesis may use CLA").

## Not Covered

- Clock tree analysis
- Hold time / min-delay paths
- Multi-cycle paths and false paths (these require SDC context)
- Power analysis
