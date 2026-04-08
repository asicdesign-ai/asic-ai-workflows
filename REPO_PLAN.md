# REPO PLAN

## Current CI coverage

- keep `repo-lint` for repository structure and markdown-link integrity
- keep `structured-files` for JSON and YAML syntax validation
- keep `skill-contracts` for skill metadata, rule references, and output examples
- keep `flow-contracts` for flow metadata, rule references, skill references, and
  output examples
- keep `eval-smoke` for schema-backed smoke asset validation

## Near-term repository direction

- continue expanding deterministic, schema-backed skills before broadening runtime
  execution
- add smoke fixtures and expected outputs whenever new skills, rules, schemas, or
  flows land
- keep DV planning artifacts grounded in RTL evidence and explicit design intent

## Current progress

- added `flows/block-level-rtl-plan/` for front-end block RTL planning
- added requirements, microarchitecture, RTL generation, lint, RDC, and package
  assembly skill contracts
- added new rules for requirements traceability, PPA capture, diagram
  selection, synthesizable RTL, lint severity, and RDC classification
- added schema-backed smoke assets for the new front-end flow
- added a chained smoke handoff proving `block-level-rtl-plan` artifacts can
  feed `block-dv-plan`

## Next repository priorities

- add a deterministic runner or harness for `block-level-rtl-plan`
- extend front-end planning with low-power and DFT-readiness skill families
- keep growing schema-backed chained examples across flows

## Deferred work

- add a Verilator compilation task later as a separate CI check
- do not add the Verilator task in the current change set
