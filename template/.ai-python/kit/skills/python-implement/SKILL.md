---
name: python-implement
description: Implement an authorized Python change with project policy, meaningful tests, docstring updates, and verification evidence. Use when starting or continuing a scoped code change, fixing a defect, adding tested behavior, or updating project source and tests.
---

# Python implementation

## Before changing code

1. Read `AGENTS.md`, `.ai-python/policy.toml`, and the architecture reference named by `[architecture].reference`.
2. Inspect the existing implementation, tests, call sites, and native configuration. Reuse maintained functionality before adding a new abstraction.
3. Confirm the change is inside authorized scope. Raise a conflict in authority, policy, or scope instead of working around it.
4. Read [engineering policy](../../references/engineering-policy.md) and, for exceptions, [exceptions](../../references/exceptions.md).

## Make the change

- Keep one cohesive behavior change per increment.
- Add or update behavioral tests with independent expected results. Add a regression case for a defect; it must fail before the fix.
- Update the docstring in the same change as behavior or signature. Use the configured format and scope.
- Keep the architecture direction intact. Change `importlinter.ini` and the architecture reference only with an explicit project decision.
- Prefer the standard library and existing functions. If a dependency is needed, stop and follow [python-dependencies](../python-dependencies/SKILL.md) and the approval process.
- Avoid broad `# noqa`, `Any`, casts, or type ignores. A narrow suppression needs a rule code and a documented reason.

## Verify and report

Run the unified check:

```sh
just --justfile .ai-python/kit/justfile --working-directory . check
```

Report the revision, command, per-stage outcomes, test and coverage summary, and any skipped or not-executed work using the [evidence format](../../references/evidence.md). Never claim a check passed without running it.

If a required check fails, fix the implementation or raise the conflict. Do not weaken the gate, delete a meaningful test, or lower a threshold to obtain a pass. See [guardrails](../../references/guardrails.md).

## Example

Positive: add a blank-name rejection in the core function, extend the normal and boundary tests, update the public docstring, and run the check.

Negative: edit only the test to accept the current output, add `# noqa: C901` to a genuinely complex function, or add `requests` without a dependency review. Stop and correct the approach instead.
