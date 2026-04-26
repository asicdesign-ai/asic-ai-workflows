# Tool Evidence Provenance

Use this rule whenever a skill consumes MCP output or other external tool output
as evidence.

## Required behavior

1. Use tools only when the user provides concrete inputs such as a project root,
   filelist, source files, report files, or generated sources materialized on
   disk.
2. Discover tools by declared capability, schema, and description. Treat MCP tool
   annotations such as read-only or destructive hints as hints, not guarantees.
3. Prefer read-only context tools for evidence collection, such as project parse,
   diagnostics, design-unit inventory, hierarchy, symbol lookup, or report
   retrieval.
4. Record tool provenance in `tool_evidence` whenever tool output is used or an
   attempted tool path is unavailable, incomplete, or returns a structured error.
5. Normalize tool findings through the skill's own schema, severity model, and
   grounding rules. Preserve original tool names, rule IDs, or severities only as
   evidence metadata.
6. If tool evidence is unavailable and no tool call is attempted, emit
   `tool_evidence: []` and continue from the provided source evidence.

## Prohibited behavior

- Do not hard-code vendor tool names or capabilities that were not exposed by
  the available tool schema.
- Do not invoke destructive, implementation-changing, signoff, synthesis,
  simulation, CDC, timing, or RTL-editing tools unless the active flow explicitly
  asks for that downstream phase.
- Do not claim lint, CDC, synthesis, timing, or signoff cleanliness from parse or
  elaboration diagnostics alone.
- Do not hide tool errors or degraded tool context by silently treating them as
  passing evidence.
