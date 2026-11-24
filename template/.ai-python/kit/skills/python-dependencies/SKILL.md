---
name: python-dependencies
description: Evaluate and review Python runtime and development dependencies, reuse options, stdlib-only exceptions, manifest and lock changes, and deptry findings. Use when adding, removing, or upgrading a dependency, resolving a dependency policy failure, or auditing declared and imported packages.
---

# Python dependencies

Read `[dependencies]` in `.ai-python/policy.toml` and the [exceptions](../../references/exceptions.md) rules. Runtime and development scopes are independent: `reuse-first`, `balanced`, `minimal`, or `stdlib-only`.

## Evaluate

1. Confirm the capability is not already provided by the standard library, the project, or a maintained dependency.
2. Compare maturity, maintenance, license, security, transitive resolution, portability, performance, and total maintenance cost.
3. Respect the selected mode. Under `stdlib-only`, every direct declaration in scope needs an exact normalized-package exception with rule `dependency.runtime` or `dependency.development`.
4. Do not add a runtime dependency merely by selecting a profile. Framework and toolkit selection stays with the project.
5. Keep the reserved `ai-python-kit` group to verification tools only. Project groups must not include it.

## Change

- Use uv-native commands and review `pyproject.toml` and `uv.lock` together.
- Do not hide dynamic or marker-disabled declarations; all direct runtime declarations are in scope.
- Check official status, errors, and decommission behavior against dependency policy.
- Run the dependency stage and the unified check:

  ```sh
  just --justfile .ai-python/kit/justfile --working-directory . check
  ```

deptry checks missing, unused, transitive, and development-only imports on production paths. Review any `[tool.deptry]` mapping or exception.

## Approval

A dependency addition may need prior approval under policy. An agent cannot grant its own exception or approve its own change. Record the exact scope, reason, owner, approver, dates, and approval reference; expired records fail the gate.

## Example

Positive: reuse an existing helper, document that the standard library is insufficient, add a scoped exception for one normalized package, update the lock, and pass deptry.

Negative: adding `pandas` for one addition, adding `requests` to a `stdlib-only` runtime without an exception, or deleting an unused declaration without checking whether the import path is dynamic.
