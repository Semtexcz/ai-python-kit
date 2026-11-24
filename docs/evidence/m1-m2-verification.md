# M1/M2 verification evidence

Recorded 2026-11-24 on Linux with Python 3.12.16. The worktree is based on `5f62c3feb16e647ca73e68d5dc387f73f6639d7b`; the implementation diff fingerprint excluding the report and evidence page is `aa988cce70a71754ad15c72dced26da6c339220ec34e50f7b9db3092732a80a0`. No release tag or remote push exists.

## Kit checks

```text
$ uv run just check
ruff format --check: 18 files already formatted
ruff check: All checks passed
mypy: Success: no issues found in 1 source file
pytest -m "not e2e and not network": 93 passed, 44 deselected
exit 0

$ uv run pytest -q
137 passed in 174.09s
exit 0
```

## Rendered project

Rendered with `copier copy --defaults`, then `uv lock`, then:

```text
$ just --justfile .ai-python/kit/justfile --working-directory . check
PASS config
PASS format
PASS lint
PASS types
PASS docs
SKIP architecture.contracts (flat graph; reason in docs/architecture.md)
PASS architecture
PASS dependencies
PASS secrets
PASS tests
SKIP online.vulnerabilities (offline mode; use 'check online')
VERIFICATION PASSED mode=offline
exit 0

$ just --justfile .ai-python/kit/justfile --working-directory . check online
PASS config
PASS format
PASS lint
PASS types
PASS docs
SKIP architecture.contracts (flat graph; reason in docs/architecture.md)
PASS architecture
PASS dependencies
PASS secrets
PASS tests
PASS online
VERIFICATION PASSED mode=online
exit 0
```

The manual seed matrix also passed offline: scientific auto (NumPy), Sphinx, PEP 257 (structured check skipped), strict, layered with and without CLI, hexagonal, custom, and the profile-conflict rejection.

## Skills

`skills-ref validate` passed for `python-implement`, `python-review`, `python-audit`, `python-verify`, `python-architecture`, `python-dependencies`, and vendored `modern-python`. Invalid YAML, missing description, and name/directory mismatch were rejected in tests.

## Tool versions

```text
Python 3.12.16
uv 0.13.9
just 1.59.0
Copier 9.19.1
Ruff 0.17.6
mypy 2.4.1
pytest 9.2.0
coverage.py 7.17.5
pytest-socket 0.8.1
pydoclint 0.12.0
Flake8 7.5.0
Import Linter 2.17
deptry 0.25.1
packaging 26.4
pip-audit 2.10.1
Gitleaks 8.30.1
skills-ref 0.1.0
```

## Not executed

GitHub Actions execution, an independent pilot adoption/update, Python 3.11, non-Linux platforms, and human approval authenticity review. These remain M3 work and are not claimed as passed. Generated environments, caches, JUnit files, audit reports, and raw logs are not committed.
