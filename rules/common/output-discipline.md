# Output Discipline

Use this rule whenever a skill emits a structured report.

## Required behavior

1. Emit exactly one YAML document and no prose before or after it.
2. Follow the schema defined by the skill exactly. If a section has no entries, emit
   an empty list `[]` or zero counts rather than omitting the section.
3. Use the skill's enum values, field names, and ID prefixes exactly as written.
4. Keep output ordering deterministic:
   - preserve source order for entities unless the skill defines a stronger sort rule
   - apply the same tie-break every time when primary sort keys are equal
5. Deduplicate repeated findings before emission. If multiple use sites refer to the
   same underlying issue, merge them into one entry when the skill schema allows it.
6. Keep free-text fields short and factual. `description` must be one sentence.
   `fix` and `suggestion` fields must be at most two sentences.
7. Prefer integers over vague ranges when the source supports an exact value.

## Prohibited behavior

- Do not add explanatory commentary outside the YAML.
- Do not create extra schema fields.
- Do not vary enum spelling, capitalization, or field ordering between runs.
