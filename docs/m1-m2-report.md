# M1/M2 implementation report

**Verdict · READY FOR M3 WITH CONDITIONS**

**Date · 2026-11-24**

M1 and M2 are implemented and locally verified on the supported Linux/Python 3.12 reference environment. M3 independent acceptance, a real CI run, pilot adoption, and release preparation remain open. This is not a release and no release tag exists.

## Executive summary

The repository now contains a working Copier overlay, a project-owned policy model, profile composition, native quality configuration, a single verification recipe, staged initialization/adoption/update procedures, six Agent Skills, and deterministic positive and negative tests. The default, CLI, scientific, strict, minimal, layered, hexagonal, and custom seeds pass the real gates. A single violation fails at the expected stage and propagates a nonzero exit code.

The main residual risk is breadth: the read-only adapter is 1,411 lines because it validates policy, direct dependencies, docstring presence, architecture applicability, category selection, and result interpretation. It remains one standard-library-plus-`packaging` module with no rule engine or plugin framework, but M3 should review whether its concerns remain proportionate.

## Implementation summary

### M1 deliverables

- Namespaced Copier template with `_subdirectory: template`, no tasks, migrations, custom Jinja extensions, or trust flag.
- `.copier-answers.ai-python-kit.yml` lineage and historical answers.
- Project-owned `.ai-python/policy.toml` and native configuration under `.ai-python/config/`.
- Kit-owned `.ai-python/kit/` with the adapter, recipe, references, skills, bootstrap material, and upstream inventory.
- Profile composition for library, CLI, scientific, backend, desktop, automation, and data processing.
- Quality seeds for minimal, standard, and strict, with explicit profile/docstring overrides.
- Architecture seeds for modular, layered, hexagonal, and custom layouts with matching Import Linter contracts or a reasoned flat mode.
- Reserved `ai-python-kit` dependency group with exact verification tool pins.
- Unified `just --justfile .ai-python/kit/justfile --working-directory . check` workflow with offline and online modes.
- Tagged update, conflict, rollback, adoption preflight, and staged promotion procedures.

### M2 deliverables

- Six canonical workflow skills: `python-implement`, `python-review`, `python-audit`, `python-verify`, `python-architecture`, `python-dependencies`.
- Shared references for engineering policy, review, evidence, guardrails, exceptions, examples, and upstream precedence.
- Root `AGENTS.md` routing block with mandatory guardrails and the verification entry point.
- Vendored Trail of Bits `modern-python` skill with CC BY-SA 4.0 license, notice, templates, and hashes.
- Pinned references for Nathan Gage `python-pytest`, `python-best-practices`, and `python-async-best-practices`; no redistribution because the MIT declaration lacks a copyright and permission notice.
- `upstream-skills.toml` provenance inventory and offline hash validation.
- Reference-validator checks for all shipped skills, including negative metadata cases.

### Pinned toolchain

Python 3.12.16 reference (3.11 minimum), Copier 9.19.1, uv 0.13.9, uv_build 0.13.9, Ruff 0.17.6, mypy 2.4.1, pytest 9.2.0, coverage.py 7.17.5, pytest-socket 0.8.1, pydoclint 0.12.0, Flake8 7.5.0, Import Linter 2.17, deptry 0.25.1, packaging 26.4, pip-audit 2.10.1, Gitleaks 8.30.1, just 1.59.0, and skills-ref 0.1.0 at `agentskills/agentskills@83021e2be457a9b6679148719c1f6074f0ad975e`. Sources, licenses, probes, and limitations are in [toolchain evidence](toolchain.md).

## Requirement traceability

| ID | Implementation | Verification evidence | Limits and remaining work |
| --- | --- | --- | --- |
| MVP-01 initialization | `copier.yml`, `template/`, `.ai-python/kit/bootstrap/` | A01–A03: `tests/test_render.py`, `tests/test_packaging.py`, baseline check | Published tag and release install path remain for M3. |
| MVP-02 adoption | `docs/lifecycle.md`, `template/.ai-python/kit/bootstrap/adopt/`, `adoption-preflight` | A10: `tests/test_adoption.py` | Full approved-baseline pilot and semantic merge review remain. |
| MVP-03 updates | Lifecycle procedure, answers file, tagged Copier update | A11: `tests/test_lifecycle.py` | Real release-tag update and pilot rollback remain. |
| MVP-04 profiles and quality | Template computed answers, `policy.toml` generation, `tests/test_render.py` | A01–A02 | Additional profile combinations are not exhaustively enumerated. |
| MVP-05 architecture and dependencies | Native config generation, adapter checks, deptry | A06–A07: `test_architecture_contracts.py`, `test_adapter_dependencies.py`, generated dependency negatives | Dynamic imports, runtime coupling, and dependency tradeoffs remain semantic. |
| MVP-06 typing and docstrings | mypy/Flake8/pydoclint config, adapter presence gates | A04–A05: generated negatives, `test_adapter_docstrings.py`, `test_docstring_formats.py` | Docstring meaning/detail and public-only typing intent remain review. |
| MVP-07 maintainability and security | Ruff complexity/security rules, coverage, Gitleaks, pip-audit | A04, A08–A09 | History scans and external advisory freshness remain operational evidence. |
| MVP-08 skills and guardrails | `template/.ai-python/kit/skills/`, references, AGENTS routing | A13–A14: `test_skills.py`, `test_provenance.py`, exception tests | Human approval authenticity and content review remain. |
| MVP-09 unified verification | `.ai-python/kit/justfile`, CI example | A12: local runs, static CI parity, failure propagation | No real GitHub Actions execution yet. |
| MVP-10 model-free acceptance | 137 deterministic tests, temporary repositories, local tags | Full local suite | Live provider smoke is isolated; no model calls are used. |
| MVP-11 portability and reproducibility | Standard packaging, uv lock, pinned actions, project ownership | A03, A11–A12 | Python 3.11 and non-Linux platforms are not in the executed matrix. |

## Acceptance evidence

Statuses are **Passed** (executed with the stated result), **Partially covered** (enforceable portion executed; review or a named case remains), **Failed** (none in final runs), or **Not executed**.

| Case | Status | Test location | Command and actual result | Remaining work |
| --- | --- | --- | --- | --- |
| A01 | Passed | `tests/test_render.py`, `tests/test_config_validation.py` | `pytest -q`; 137 passed. Renders valid/custom profiles; rejects bad names, paths, enums, unknown keys, empty scope, and unresolvable config. | Published tag path. |
| A02 | Passed | `tests/test_render.py` | Library+CLI+Scientific gives CLI, NumPy, contracts; Backend+Desktop auto fails; explicit layered passes; strict/minimal preserve overrides and seeds. | More combinations only if added to support. |
| A03 | Passed | `tests/test_generated_project.py`, `tests/test_packaging.py` | Baseline check passes; wheel installs and imports without kit/dev deps; CLI runs valid and invalid input. | None within reference matrix. |
| A04 | Passed | `tests/test_generated_project.py` | Formatting, F401, C901, PGH003, S307, return type, unused ignore, redundant cast, implicit optional, and explicit `Any` fail at expected stages. | None. |
| A05 | Passed | `tests/test_adapter_docstrings.py`, `tests/test_docstring_formats.py`, `tests/test_native_plugins.py`, generated docs negatives | Presence/scope/property/async/tests/overload cases pass; Google, NumPy, and Sphinx wrong names fail; PEP 257 reports the structured skip; D205 fails; a venv without pydoclint fails the required-plugin check. | Docstring meaning/detail and public prose remain semantic review. |
| A06 | Passed | `tests/test_architecture_contracts.py`, `tests/test_render.py` | Layered transitive, hexagonal direct, modular cycle, custom forbidden, custom positive, and flat-with-two-children cases behave as specified. | Runtime coupling remains review. |
| A07 | Passed | `tests/test_adapter_dependencies.py`, `tests/test_generated_project.py` | stdlib-only runtime/dev, marker/optional declarations, exact/expired exceptions, reserved-group misuse, unresolved include, dynamic metadata, and DEP001–DEP004 negatives. | Transitive effects of an approved exception remain review. |
| A08 | Passed | `tests/test_generated_project.py`, `tests/test_results.py` | Default unit+regression selection, selected integration category, socket denial, empty selection, all-skipped JUnit, and coverage threshold failure. | Additional property/stochastic tooling remains opt-in. |
| A09 | Passed | `tests/test_generated_project.py`, `tests/test_results.py` | Stale/missing lock, synthetic Gitleaks match, ignored evidence path, broken executable, offline skip, injected clean/fail/skip/unavailable audit fixtures, and live online audit. | Advisory result is scoped to provider and time. |
| A10 | Passed | `tests/test_adoption.py`, `tests/test_generated_project.py` | Preflight refuses dirty/colliding/symlink targets; overlay integration preserves source/tests/instructions and other kit namespaces; duplicate native config fails; an exact native suppression with a scoped exception passes while a fresh violation fails. | Real pilot merge and semantic review remain. |
| A11 | Passed | `tests/test_lifecycle.py` | Tagged update preserves project-owned source/tests/instructions; managed content updates; overlap produces `.rej`; rollback restores the checkpoint; incompatible schema fails. | Real release tags remain. |
| A12 | Partially covered | `tests/test_ci_workflow.py`, generated failure tests | Local command and stages pass; failure propagation and `NOT EXECUTED` lines verified; missing and broken executable cases fail secrets; workflow pins, permissions, and online job checked statically. | No GitHub Actions execution. |
| A13 | Passed | `tests/test_skills.py`, `tests/test_provenance.py` | All shipped skills pass `skills-ref validate`; invalid YAML, missing description, and name/directory mismatch fail; hashes, files, notices, and reference-only entries match. | Content and license review remain human. |
| A14 | Partially covered | `tests/test_adapter_dependencies.py`, `tests/test_config_validation.py` | Missing fields, duplicate IDs, bad/reversed dates, expired records, unknown fields, and normalized targets fail. | Approval authenticity and final scope remain human acceptance. |

## Architectural deviations

| Deviation | Reason | Impact and approval |
| --- | --- | --- |
| Shared docstring macros live at the repository root, outside `template/`, and are imported with `with context`. | Copier's Jinja loader resolves includes from the source root while rendering the `template/` subdirectory. | Implementation detail; no requirement change. |
| The modular/custom core-direction contract is generated only when a CLI module exists. | A contract naming a nonexistent module cannot be meaningful; flat mode already skips contracts. | No requirement change; custom contract mode still has an acyclic contract and the seed passes. |
| The hexagonal CLI entry is package-root `cli.py` and uses the console adapter directly; the composition root remains a separately tested wiring point. | A CLI adapter importing the composition root while the composition root imports adapters created an Import Linter sibling cycle. | The dependency direction stays inward and contracts pass; no approval needed. |
| An empty runtime export is accepted as a valid audit graph. | A project with no runtime declarations has nothing to audit. | The verification graph is still audited; malformed or skipped provider data fails. |
| Native exception records are validated but not translated into tool flags by the adapter. | Flags and exact native suppressions remain project-owned and reviewable; a translator would become a rule engine. | A07/A10/A14 record the semantic/human portion. |
| `lint-imports --config` is retained despite a deprecation warning in Import Linter 2.17. | The verification contract names that command and the pinned version supports it. | Revisit at the next pin; positional form is the migration. |

No deviation requires a material architecture or requirement change. The maintainer should confirm the adapter breadth and the native-exception boundary at M3.

## Maintainability assessment

- Custom Python: one 1,411-line adapter module, 2,750 lines of tests, no runtime package or public CLI. The adapter uses the standard library plus `packaging` for PEP 508 parsing.
- Adapter responsibilities: policy shape and cross-reference validation, direct dependency modes and exception matching, docstring presence by AST, architecture mode and flat eligibility, pytest selector construction, JUnit and audit result interpretation, adoption preflight, and path/sync argument output.
- Significant interfaces: `validate`, `dependencies`, `docstrings`, `pytest-selector`, `architecture-mode`, `sync-args`, `paths`, `junit-check`, `audit-check`, `adoption-preflight`.
- New kit development dependencies: Copier, pytest, Ruff, mypy, coverage, packaging, and `rust-just`. Generated projects pin the reserved verification group; they add no runtime dependency from profile selection.
- Overengineering risk: the adapter is broad. Each check answers a named requirement, and no generic rule engine, plugin system, configuration merger, or task runner was introduced. M3 should review whether splitting validation from result interpretation improves maintainability without adding coordination cost.
- Simplification opportunities: reuse the same path enumeration in more subcommands, reduce duplicate exception record scanning, and consider a small typed policy model if the adapter grows. Do not add a framework.

Additional command excerpts and tool versions are recorded in [M1/M2 verification evidence](evidence/m1-m2-verification.md).

## Verification results

- **Revision/worktree identity** · Worktree on `5f62c3feb16e647ca73e68d5dc387f73f6639d7b`; implementation diff fingerprint (excluding this report and its evidence page) `aa988cce70a71754ad15c72dced26da6c339220ec34e50f7b9db3092732a80a0`. Changes are uncommitted; no remote push, tag, or release was performed.
- **Interpreter and tools** · Python 3.12.16; versions in [toolchain evidence](toolchain.md).
- **Commands executed** ·
  - `just check` in the kit repository: exit 0; 93 passed, 44 deselected.
  - `pytest -q` in the kit repository: exit 0; 137 passed in 174.09s.
  - Rendered default project `just --justfile .ai-python/kit/justfile --working-directory . check`: exit 0; config, format, lint, types, docs, architecture, dependencies, secrets, and tests passed; architecture contracts skipped for the reasoned flat graph; online skipped by mode.
  - Rendered default project `check online`: exit 0; `PASS online`; no advisories for the audited graphs at run time.
  - Manual seed matrix: default, scientific auto, Sphinx, PEP 257, strict, layered, hexagonal, and custom all exit 0 on the offline check.
  - `skills-ref validate` on six kit skills and `modern-python`: all valid.
- **Tests and coverage** · 137 tests pass. The generated baseline reports 100.00% line and branch coverage; coverage thresholds are enforced for generated projects. No kit-level coverage percentage is claimed.
- **Skipped by policy or mode** · online vulnerabilities in offline mode; architecture contracts for flat packages; pydoclint structured checks for PEP 257; e2e/network tests are separated from the default kit check.
- **Unexecuted** · GitHub Actions execution, independent pilot adoption and update, Python 3.11 matrix, non-Linux platforms, and human approval authenticity checks.
- **Failed final checks** · none within the executed scope.
- **Remaining defects** · none known in the executed scope. The unexecuted cases above are not claims of success.

## M3 handoff

### Independent review targets

- Adapter breadth, complexity, and the native-exception boundary.
- Profile composition edge cases and architecture seed proportionality.
- CI workflow correctness on GitHub-hosted runners, including action pins and cache behavior.
- Adoption merge safety and update conflict recovery on a real repository.
- Docstring meaning, test-oracle quality, dependency tradeoffs, and scientific guidance.

### Remaining acceptance work

- Execute A10 approved legacy-baseline pilot and semantic merge review.
- Execute A12 on real CI, including a genuinely missing executable and a protected-branch review.
- Complete A14 human approval authenticity and final-content review.
- Confirm Python 3.11 and any additional supported platform before claiming them.

### Recommended pilot

1. Select one representative existing single-package project with static PEP 621 metadata and a clean Git checkpoint.
2. Render the adoption proposal on an adoption branch; run preflight and diff review.
3. Copy only the overlay, merge routing/CI/native ownership changes, and record any scoped baseline exceptions with owners and expiry.
4. Run the offline check and a pilot CI branch; fix real conflicts rather than weakening gates.
5. Update between two reviewed tags in a throwaway branch; verify preserved customizations, `.rej` visibility, and rollback.
6. Record the pilot revision, commands, exceptions, and remaining findings.

### Known risks and release prerequisites

- No release tag exists; the documented `v0.1.0` source is a placeholder.
- The kit's own release license remains a maintainer decision; third-party notices are present.
- The adapter's breadth may warrant simplification after independent review.
- `lint-imports --config` emits a deprecation warning at the pinned version.
- Dependency advisory results are time- and provider-dependent; release needs a fresh online audit.
- GitHub Actions pins and the supported matrix must be confirmed at release.
- Release requires M3 acceptance, a maintainer license decision, a signed-off compatibility/notice record, and explicit publish authorization.
