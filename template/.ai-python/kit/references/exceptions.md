# Approvals and exceptions

An agent cannot grant its own exception. A structurally valid record does not prove that a human approved the final content; the approval reference and review identity must be checked.

## Record shape

```toml
[[exceptions]]
id = "dep-requests-001"
rule = "dependency.runtime"
target = "requests"
reason = "The service requires the maintained HTTP client selected in ADR-004."
owner = "platform-team"
approved_by = "maintainer-name"
approved_on = "2026-11-24"
expires_on = "2027-03-31"
approval_ref = "https://example.invalid/decisions/1234"
```

Every record needs a stable unique `id`, exact `rule`, narrow `target`, `reason`, accountable `owner`, human `approved_by`, ISO `approved_on` and `expires_on` dates, and `approval_ref` identifying the decided scope. Dates are UTC and effective through `expires_on`.

## Rules

- `dependency.runtime` and `dependency.development` use exact normalized package names for `stdlib-only` mode.
- Native exceptions use the exact tool rule code and a specific path, object, or import edge.
- An expired record fails the applicable gate. It never permits a violation after expiry.
- An unapproved proposal remains in discussion and grants nothing.
- Review dependency additions and lock diffs even when no exception is needed.
- Point the record at the implementing narrow suppression when one exists.
- Maintainers review mappings where tool output has no stable identity.

## Scope

Prefer a path, object, or import pair over a package-wide exclusion. A baseline exception for adopted technical debt records the original finding, owner, tracking reference, current threshold or scope, and expiry. Keep active gates for unaffected code.

## Limits

The adapter validates shape, matching, duplicates, and dates. It cannot authenticate the approver or prove that the approval covers the final diff. That is a human acceptance step.
