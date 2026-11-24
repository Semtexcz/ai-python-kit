# Engineering policy map

Project-owned instructions in `AGENTS.md` and `.ai-python/policy.toml` govern. Kit workflow instructions come next; reviewed upstream recommendations are advisory.

## Authoritative locations

| Concern | Source |
| --- | --- |
| Profiles, quality preset, module map, review thresholds, exceptions | `.ai-python/policy.toml` |
| Ruff lint and format | `.ai-python/config/ruff.toml` |
| mypy scope and strictness | `.ai-python/config/mypy.ini` |
| pydoclint diagnostics and docstring style | `.ai-python/config/flake8.ini` |
| Import contracts | `.ai-python/config/importlinter.ini` |
| Gitleaks rules and exclusions | `.ai-python/config/gitleaks.toml` |
| pytest markers and options | `.ai-python/config/pytest.ini` |
| Coverage mode and threshold | `.ai-python/config/coverage.ini` |
| Runtime and development declarations | `pyproject.toml` and `uv.lock` |
| Dependency import diagnostics | `[tool.deptry]` in `pyproject.toml` |

Do not duplicate these settings in a second file. The unified check passes native paths explicitly.

## Architecture

`[architecture].style` is `modular`, `layered`, `hexagonal`, or `custom`. `[architecture].reference` names the project-owned boundary document. `[architecture].graph` is `contracts` or `flat`.

Use `flat` only when the package has no intended internal boundary and at most one immediate importable production child (excluding `__init__.py`). Record the reason in the reference. Any other layout uses `contracts` with at least one meaningful Import Linter contract. Keep runtime imports and configuration-based coupling consistent with the static graph.

## Dependencies

Runtime and development modes are independent: `reuse-first`, `balanced`, `minimal`, or `stdlib-only`. The reserved `ai-python-kit` group contains verification tools only. Project groups must not include it, and it must not contain application dependencies.

For `stdlib-only`, every direct declaration in that scope needs an exact normalized-package exception with rule `dependency.runtime` or `dependency.development`. Markers and extras do not exempt a declaration. Transitive dependencies introduced by an approved exception still need review. deptry checks missing, unused, transitive, and development-only imports in production code.

## Typing

`[typing].annotation_scope` records API intent. The mypy configuration is authoritative for checked modules and strictness. All levels check untyped bodies, implicit optional, unused ignores, and redundant casts. Standard requires definitions on production modules. Strict enables the pinned strict preset and explicit-`Any` diagnostics.

Review every `Any`, cast, and ignore for a demonstrated boundary. Prefer real types or validation. Ruff `PGH003` requires a specific rule code on a suppression.

## Docstrings

`[docstrings].format` is `google`, `numpy`, `sphinx`, or `pep257`. `scope` is `public`, `all`, or `custom`; `custom` requires a nonempty `categories` list from `modules`, `classes`, `functions`, `methods`, `properties`, and `tests`. `public_detail` and `private_detail` are independent.

The adapter checks nonempty presence for the effective scope, including async definitions and property getters. Flake8 with pydoclint checks structured signatures except for `pep257`, where the structured check is skipped by policy. Semantic review covers meaning, completeness, units, and factual accuracy. A structurally valid docstring with the wrong units is still wrong.

## Testing

`[testing].categories` selects `unit`, `integration`, `regression`, `property`, and `end_to_end`. Unmarked tests count as unit. `external`, `stochastic`, and `performance` are always excluded from the default selector. Add approved plugin import names to `[testing].plugins`.

Default tests deny Python socket creation through pytest-socket. Use temporary resources, restore mutable state, seed randomness, inject clocks, and use failure-bound timeouts. Never add reruns to hide flakes. Coverage uses the native `branch` and `fail_under` settings. A correction needs a regression test that would fail before the fix.

## Exceptions

Policy exceptions are `[[exceptions]]` records in `.ai-python/policy.toml`. They require an exact rule and target, a reason, an owner, a human approver, dates, and an approval reference. Expired records fail verification. See [exceptions](exceptions.md).

## Verification limits

The check proves only the recorded revision and measured scope. It cannot authenticate an approver, judge intent, prove scientific correctness, or inspect external advisory freshness in offline mode. Runtime coupling, test quality, docstring meaning, dependency tradeoffs, and design suitability need review.
