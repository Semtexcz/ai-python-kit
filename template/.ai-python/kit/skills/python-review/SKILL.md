---
name: python-review
description: Review a concrete Python diff independently of its author, checking behavior, tests, docstrings, architecture, dependencies, security, and verification evidence. Use when asked to review a change, assess a pull request, or decide whether a diff is ready for acceptance.
---

# Python review

Review the actual diff and evidence, not the author's summary. Use the [review checklist](../../references/review-checklist.md) as the coverage map.

## Workflow

1. Establish the base and reviewed revision. Inspect the diff, affected files, and call sites.
2. Read `.ai-python/policy.toml`, the architecture reference, and applicable exceptions.
3. Run or inspect the unified check on the reviewed revision when it is available and safe to execute:

   ```sh
   just --justfile .ai-python/kit/justfile --working-directory . check
   ```

4. Verify that tests are behavioral, deterministic, and independent of the implementation. Check that a regression test fails on the parent revision.
5. Check architecture direction, dependency justification, typing suppressions, docstring accuracy, input validation, secret handling, and error behavior.
6. Distinguish observed violations, recommendations, accepted exceptions, and unknowns.

## Report

Name the reviewer and reviewed revision, inspected files, commands actually run, findings with severity, path, evidence, and remedy, disposition, and remaining gaps. Follow the [evidence format](../../references/evidence.md).

Do not approve your own change, authenticate an approval, or claim a stage passed without output. A structurally valid exception does not prove authorization; see [exceptions](../../references/exceptions.md).

## Examples

Positive finding: "Major - pkg/cli.py:44: `parser.error` converts an unexpected transport failure into exit 2. Keep unexpected failures distinct and test both paths."

Negative review behavior: accepting a deleted assertion because the new output "looks right", or reporting the lint stage as passed because only the author said so. Require the actual result and the behavior-preserving justification.
