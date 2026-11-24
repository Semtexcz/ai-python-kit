---
name: python-audit
description: Audit a Python project for recurring engineering risks, policy fit, exception scope, gate evidence, and missing controls. Use for project-level health checks, adoption baselines, technical-debt review, or periodic policy audits, not for reviewing a single small diff.
---

# Python audit

An audit works at repository scope. Reuse the [review checklist](../../references/review-checklist.md) for individual findings and the [evidence format](../../references/evidence.md) for the report.

## Scope

1. Identify the analyzed revision, profiles, quality level, architecture style, dependency modes, docstring scope, test categories, and coverage threshold.
2. Inspect policy and native configuration ownership for duplicates or conflicting authority.
3. Inspect architecture contracts and whether the mapped modules match the actual package.
4. Review dependency declarations, lock changes, the reserved verification group, and every exception's scope and expiry.
5. Review gate evidence for the recorded revision, including skipped and not-executed stages.
6. Look for recurring patterns: repeated suppressions, duplicated implementations, weak oracles, flaky tests, hidden failures, undocumented public behavior, and stale baselines.

## Report

Keep these categories distinct:

- Observed violations with evidence.
- Recommendations and tradeoffs.
- Accepted exceptions with IDs and scope.
- Unknowns that need access, execution, or human judgment.

Disposition is a recommendation. Approval authenticity and final acceptance remain with the maintainer. Do not grant or renew an exception on the maintainer's behalf.

## Example

Positive: "Two native coverage configurations exist; CI and local checks can disagree. Redirect CI to `.ai-python/config/coverage.ini` and remove the duplicate."

Negative: treating an expired dependency exception as accepted because the TOML is well-formed, or reporting an offline audit as proof of current advisory status.
