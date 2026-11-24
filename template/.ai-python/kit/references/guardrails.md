# Guardrails and authority

## Prohibited agent behavior

- Weakening tests, gates, or policy to make an incorrect implementation pass.
- Broad lint suppressions, or typing bypasses with `Any`, casts, or ignores without a demonstrated boundary.
- Hiding exceptions, suppressing failures, or reporting success without execution evidence.
- Duplicate implementations, speculative abstractions, or scope expansion.
- Unauthorized dependencies or architecture-contract violations.
- Filler docstrings or test expectations derived from the implementation under test.
- Low-value coverage inflation or flaky substitutes for real assertions.
- Self-approved exceptions or self-authorized scope changes.

## Division of evidence

| Kind | What it can establish | Limits |
| --- | --- | --- |
| Deterministic validation | Selected rule violations, gate outcomes, exact exit codes | Only configured scope and recorded revision |
| Semantic review | Intent, design fit, test quality, docstring accuracy, suppression scope | Needs a reviewer and inspected evidence |
| Human approval | Authorization for an exception or acceptance | Cannot be proven by a structural record alone |

An agent's description of its permissions does not establish authority. Approval authenticity and final acceptance stay with the maintainer. Structural validation can check an exception's shape, matching, dates, and references; it cannot authenticate the approver or prove that the decision covers the final content.

## Reporting

Cite affected behavior, policy, and verification results. Keep passed, failed, skipped, and not-executed outcomes distinct. Preserve pending evidence when a required check did not run.
