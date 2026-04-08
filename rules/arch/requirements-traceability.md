# Requirements Traceability

Use this rule whenever a skill turns user requirements into specifications, RTL,
or final handoff artifacts.

## Required behavior

1. Assign deterministic requirement IDs in `REQ-NNN` format and preserve them
   across downstream artifacts.
2. Keep each requirement atomic. Split combined statements when function, timing,
   or implementation intent would otherwise be ambiguous.
3. Trace every spec section, RTL fragment, and audit finding back to one or more
   explicit requirement IDs when the relationship exists.
4. When one output depends on an unstated requirement, emit an unresolved item
   instead of inventing hidden requirements.
5. Preserve the distinction between functional requirements and PPA constraints.

## Prohibited behavior

- Do not drop requirement IDs when moving from intake to spec, RTL, or package.
- Do not merge unrelated requirements under one trace record.
- Do not claim a trace link without explicit support in the provided inputs.
