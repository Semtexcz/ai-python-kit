# Evidence examples

These examples show the expected shape. Replace paths, revisions, and findings with actual evidence.

## Implementation report

```text
Change: Reject blank display names in the greeting use case.
Revision: 9a1c2d4
Policy: schema 1; profiles library, cli; quality standard

Implementation:
- Added validation in pkg/core.py and kept the CLI boundary thin.
- Added normal, whitespace, and blank-name tests; the blank-name case is the
  regression case for the reported defect.
- Updated the public docstring; no new dependency.

Verification:
PASS config / format / lint / types / docs / architecture / dependencies / secrets / tests
SKIP online.vulnerabilities (offline mode)
Coverage: line 100.00%, branch 100.00%
Exit: 0
Remaining: none.
```

## Review report

```text
Reviewer: independent reviewer
Revision: 9a1c2d4
Inspected: pkg/core.py, pkg/cli.py, tests/test_greeting.py, policy, tool output

Findings:
1. Major - pkg/cli.py: parser.error() is used for unexpected I/O failure, which
   hides a real error as a usage error. Keep I/O failures distinct.
2. Minor - tests/test_cli.py: the stderr assertion checks only a substring.
   Assert the complete diagnostic where it is stable.

Verified:
- The blank-name regression fails on the parent revision and passes here.
- Architecture and dependency stages passed on the recorded revision.

Disposition: changes requested. No exception is claimed.
```

## Audit report

```text
Scope: repository at 9a1c2d4; profiles library, cli; quality standard
Analyzed: policy, native configs, exceptions, recent changes, gate evidence

Observed:
- One expired dependency exception blocks the dependency gate.
- Coverage threshold is below the quality seed without a recorded baseline.
Recommendations:
- Renew or remove the exception through maintainer approval.
- Record the baseline scope and expiry, or restore the seed threshold.
Unknowns:
- Live advisory freshness was not checked in this offline audit.
Accepted exceptions: none beyond the two pending decisions above.
```

## Verification report

```text
Command: just --justfile .ai-python/kit/justfile --working-directory . check online
Revision: 9a1c2d4 (clean)

PASS config
PASS format
PASS lint
PASS types
PASS docs
PASS architecture
PASS dependencies
PASS secrets
PASS tests (18 passed)
PASS online (runtime and verification graphs audited; no advisories at 2026-11-24T14:00Z)
Exit: 0

Limits: the online result is scoped to the provider and time above. Semantic
review of test oracles and docstring meaning remains pending.
```

## Negative cases

A negative report is still evidence. Show the passing baseline, the single introduced violation, the failing stage and diagnostic, and the restored baseline. Never report a negative case as passed because a prerequisite failed for another reason.
