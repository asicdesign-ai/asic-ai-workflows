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

## Deferred work

- add a Verilator compilation task later as a separate CI check
- do not add the Verilator task in the current change set
