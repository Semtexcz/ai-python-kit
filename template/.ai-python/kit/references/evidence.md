# Verification evidence

Report evidence for the actual revision or worktree. Do not infer success from missing output.

## Status vocabulary

- **Passed**: the check ran and met its contract.
- **Failed**: a violation, setup error, or execution error.
- **Skipped**: an explicit mode or applicability decision with a reason.
- **Not executed**: pending after a failure, cancellation, or lost evidence.

A missing required entry is **not executed**, never passed.

## Required fields

- Revision or worktree identity and dirty-tree status.
- Policy schema and template revision.
- Interpreter and tool versions.
- Command and mode, for example `just --justfile .ai-python/kit/justfile --working-directory . check`.
- One outcome and exit code per stage: config, format, lint, types, docs, architecture, dependencies, secrets, tests, online.
- Test counts and coverage summary.
- Applicable exception IDs.
- Remaining findings and unexecuted checks.

## Example

```text
Revision: 4f2c1a9 (dirty: no)
Policy schema: 1; template: v0.1.0
Python: 3.12.16; uv: 0.13.9; just: 1.59.0; Gitleaks: 8.30.1
Command: just --justfile .ai-python/kit/justfile --working-directory . check

PASS config
PASS format
PASS lint
PASS types
PASS docs
PASS architecture
PASS dependencies
PASS secrets
PASS tests (42 passed; line 93.1%, branch 88.4%)
SKIP online.vulnerabilities (offline mode)
Exit: 0
```

For a failed run, record the failed stage and exit code, then list later stages as not executed. Keep the local result scoped to the measured revision. An online audit is a result for its provider and time, not a permanent claim.
