# Toolchain evidence

Pinned releases selected for M1/M2 and validated locally on Linux with Python 3.12.16. License identifiers come from package metadata or the upstream repository at the reviewed revision. A release record still needs the maintainer's license and notice review.

## Pins

| Tool | Version | License | Source and install |
| --- | --- | --- | --- |
| Python | 3.12.16 reference; 3.11 minimum | PSF-2.0 | uv-managed CPython or system interpreter |
| Copier | 9.19.1 | MIT | PyPI: `uv tool install copier==9.19.1` |
| uv | 0.13.9 | MIT OR Apache-2.0 | Astral release / uv installer |
| uv_build | 0.13.9 | MIT OR Apache-2.0 | PyPI build requirement |
| Ruff | 0.17.6 | MIT | PyPI `ruff==0.17.6` |
| mypy | 2.4.1 | MIT | PyPI `mypy==2.4.1` |
| pytest | 9.2.0 | MIT | PyPI `pytest==9.2.0` |
| coverage.py | 7.17.5 | Apache-2.0 | PyPI `coverage==7.17.5` |
| pytest-socket | 0.8.1 | MIT | PyPI `pytest-socket==0.8.1` |
| pydoclint | 0.12.0 | MIT | PyPI `pydoclint==0.12.0` |
| Flake8 | 7.5.0 | MIT | PyPI `flake8==7.5.0` |
| Import Linter | 2.17 | BSD-2-Clause | PyPI `import-linter==2.17` |
| deptry | 0.25.1 | MIT | PyPI `deptry==0.25.1` |
| packaging | 26.4 | Apache-2.0 OR BSD-2-Clause | PyPI `packaging==26.4` |
| pip-audit | 2.10.1 | Apache-2.0 | PyPI `pip-audit==2.10.1` |
| Gitleaks | 8.30.1 | MIT | GitHub release `gitleaks_8.30.1_linux_x64.tar.gz` |
| just | 1.59.0 | CC0-1.0 | `rust-just==1.59.0` or casey/just release binary |
| skills-ref | 0.1.0 | Apache-2.0 | Git `agentskills/agentskills@83021e2be457a9b6679148719c1f6074f0ad975e`, `skills-ref` subdirectory |
| actions/checkout | v7.0.1 | GitHub terms | SHA `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| astral-sh/setup-uv | v10.4.0 | GitHub terms | SHA `1db35dd8eee11c5894872e0b383ae6c406cf738d` |

The generated project pins the verification group exactly and lets `uv.lock` record the transitive graph. Copier, just, Gitleaks, and `skills-ref` are standalone tools, not runtime project dependencies.

## Commands and observed behavior

| Probe | Result |
| --- | --- |
| `copier copy --defaults`, then `copier update --vcs-ref TAG --conflict rej --skip-answered` between local tags | Renders, refreshes answers, preserves project-owned files, leaves a `.rej` on overlapping managed content. No Copier tasks are needed. |
| `copier copy -d creation_mode=adopt` | Renders overlay, policy, native config, bootstrap, and lineage only; root seed files are excluded. |
| `uv lock --check --offline` and `uv sync --locked --offline --no-default-groups --group ai-python-kit` | Detects a stale or missing lock and replays a warmed cache without rewriting tracked files. |
| `uv export --locked --no-default-groups --no-dev --no-emit-project --no-hashes --format requirements-txt` | Exports runtime and verification graphs for auditing. An empty runtime graph is valid for a project without runtime declarations. |
| `ruff format --check`, `ruff check` with explicit config | Detects formatting, lint, complexity, suppression-code, and security rules at the configured thresholds. |
| `mypy --config-file` with standard and strict seeds | Enforces typed production definitions, check-untyped bodies, implicit optional, unused ignores, redundant casts, and explicit `Any` at strict. |
| `flake8 --require-plugins pydoclint --config` with `style = google|numpy|sphinx` | Checks selected `DOC` diagnostics and signatures. `pep257` is reported as a policy skip for the structured check. |
| `lint-imports --config` with layers, forbidden, and acyclic-siblings contracts | Keeps valid directions and reports direct and transitive forbidden edges and cycles. `--config` is deprecated in 2.17 but remains the documented command. |
| `deptry` with `[tool.deptry]` | Reports missing (`DEP001`), unused (`DEP002`), transitive (`DEP003`), and development-only (`DEP004`) imports on production paths. |
| `pytest` with `-p pytest_socket --disable-socket` and JUnit XML | Denies Python socket creation and exposes zero/all-skipped suites through the adapter. |
| `coverage run`/`report` with native ConfigParser file | Applies line or branch mode and `fail_under`; a threshold failure stops the tests stage. |
| `gitleaks dir --redact=100 --config` | Detects synthetic provider credentials in the worktree, honors ignored cache/evidence paths, and fails on a broken executable. |
| `pip-audit --no-deps --disable-pip --strict --format json` on exported graphs | Reports advisories, returns nonzero on vulnerability findings, and leaves malformed or skipped provider data visible to the adapter. |
| `skills-ref validate` on every shipped skill | All six kit skills and the vendored `modern-python` skill pass metadata validation at the pinned revision. |

## Known limitations

- Gitleaks scans the current worktree with provider rules; it does not prove history is clean. History scans are separate.
- pytest-socket controls Python socket creation in the test process. Native libraries, subprocesses, and explicit opt-outs are outside that guarantee.
- Import contracts cover statically visible imports. Dynamic imports and configuration-based coupling need review.
- mypy scope is module-based. Public-only or per-object intent uses `[typing].annotation_scope` plus review.
- pydoclint checks structure and names, not whether the described behavior, units, or assumptions are correct.
- deptry uses static import scanning; plugins, subprocess use, and dynamic imports need review.
- pip-audit results depend on the provider and time of the run. Offline mode does not claim current advisory status.
- The supported acceptance target is Linux with Python 3.12. Python 3.11 is the declared minimum but is not yet in the executed matrix.
