---
name: python-verify
description: Run the unified Python verification workflow and report truthful per-stage outcomes. Use when asked to verify a revision, reproduce a CI failure, confirm a change locally, or determine whether checks are passed, skipped, failed, or not executed.
---

# Python verification

There is one workflow. Do not invent a parallel gate or weaken stage criteria.

## Commands

Offline, deterministic checks:

```sh
just --justfile .ai-python/kit/justfile --working-directory . check
```

Default checks plus live dependency vulnerability data:

```sh
just --justfile .ai-python/kit/justfile --working-directory . check online
```

Policy-only validation before dependencies are installed:

```sh
just --justfile .ai-python/kit/justfile --working-directory . validate
```

## Outcomes

- **Passed**: the stage ran and met its contract.
- **Failed**: a violation, setup error, or execution error.
- **Skipped**: an explicit mode or applicability decision with a reason.
- **Not executed**: pending after a failure, cancellation, or lost evidence.

Never infer a pass from absent output. Return a nonzero exit code when a required check fails. Do not bypass a missing executable, stale lock, missing plugin, or unavailable provider by editing the recipe.

## Report

Record the revision and dirty status, command and mode, tool versions, each stage and exit code, tests and coverage, exception IDs, and remaining gaps. Use the [evidence format](../../references/evidence.md).

Keep online results separate from deterministic offline claims. An online audit describes the provider and time of that run. Offline mode reports online as skipped, not passed.

## Example

Positive: `check` stops at `types` with exit 1, reports later stages as not executed, and preserves the mypy diagnostic.

Negative: running only Ruff and declaring "verification passed", or describing an unavailable advisory service as "no vulnerabilities found".
