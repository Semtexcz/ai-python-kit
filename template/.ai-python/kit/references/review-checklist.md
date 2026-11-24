# Review checklist

Use this for `python-review` and `python-audit`. Review the actual diff and evidence, not the author's summary.

## Change fit

- Does the change match the request and stay inside authorized scope?
- Is existing functionality reused instead of duplicated?
- Is the design the simplest one that satisfies current behavior?
- Are public interfaces and observable behavior clear?

## Correctness and tests

- Trace behavior through call sites, boundaries, and error paths.
- Are tests behavioral and deterministic, with independent expected results?
- Do boundary, invalid, and regression cases cover the actual risk?
- Are mocks limited to real boundaries? Is socket or clock control explicit?
- Does coverage reflect meaningful code rather than inflated assertions?

## Architecture and dependencies

- Do imports follow the stated direction and contracts?
- Is the boundary proportionate to the project, without speculative layers?
- Are new dependencies justified, licensed, maintained, and compatible with the selected mode?
- Are manifest and lock changes reviewed, including transitive effects?
- Is the reserved verification group free of application dependencies?

## Types, docs, and security

- Are annotations meaningful, with any `Any`, cast, or ignore justified and narrow?
- Do docstrings describe real behavior, units, assumptions, errors, and side effects?
- Are inputs validated and errors explicit without hidden failures?
- Are secrets, credentials, and sensitive data kept out of code, logs, and fixtures?
- Are suppressions exact and linked to an approved exception when policy requires it?

## Evidence and disposition

- Was the applicable check executed on the recorded revision?
- Are passed, failed, skipped, and not-executed outcomes truthful?
- Are exceptions valid, scoped, unexpired, and approved by a human?
- List findings with severity, path, evidence, and remedy.
- Keep observed violations, recommendations, accepted exceptions, and unknowns separate.
