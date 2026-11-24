# Verification and acceptance

The v0.1.0 workflow combines repeatable tool results, semantic review, and maintainer acceptance. See the [implementation plan](implementation-plan.md) for sequencing.

## Entry point

From the project root, local users and CI invoke:

```sh
just --justfile .ai-python/kit/justfile --working-directory . check
```

The project can expose a root alias that delegates to this command. The default `check` uses a pinned interpreter and tool versions and sets `UV_PROJECT_ENVIRONMENT=.ai-python/.venv` for verification. Document the online sync that warms dependencies. Read schema and sync inputs with the pinned interpreter and standard library before activating project dependencies. Verify lock freshness and sync the reserved group and exact selected project groups/extras from the warmed cache with locked, offline mode and default groups disabled. Then run tools through `uv run --no-sync` with the pinned Python version. The check may create or update ignored environments, caches, and evidence files. Tracked files must stay byte-identical. Clear inherited tool options that could change results, for example `PYTEST_ADDOPTS`, `PYTEST_PLUGINS`, and network allowlists. Disable pytest plugin autoload and explicitly load pytest-socket and approved project plugins. Record optional project plugin import names as strings in `[testing].plugins`.

Use the same recipe with `check online` for the default checks plus live vulnerability data. The default workflow runs on pull requests with a read-only token and no secrets or model calls. A separate scheduled or dependency-change job runs the online variant. Require an online result on release and material dependency changes. Workflow choices may select when to run a mode. All checks and criteria within each mode belong to the recipe.

| Stage | Commands and check contract |
| --- | --- |
| Configuration and repository | Validate policy and native file/contract references. Use `uv lock --check` and locked offline sync. Reject invalid configuration, missing prerequisites, or stale lock. Verify the supported repository shape, selected package, source and test paths, and root integration references. |
| Format and lint | Use Ruff `format --check` and `check` with the explicit native config on configured source/test paths. Check maintainability, docstring formatting, risky constructs and suppression codes here. |
| Types | Run mypy with `--config-file` and the native scope. |
| Docstring presence and signatures | Run the policy presence check. Run Flake8 with `--require-plugins pydoclint`, explicit config, and the selected style on matching files, or report its PEP 257 inapplicability. |
| Architecture | Run `lint-imports --config` on the installed package when contracts apply. Emit the reason for any flat-package skip. |
| Dependencies | Check direct declarations and approval scopes. Run deptry over production code, with its project-owned options. |
| Secrets | Run `gitleaks dir --redact=100 --config` against the working tree using upstream defaults and explicit cache/VCS exclusions, including `.git`, isolated verification environments and tool caches. Record scan scope. History scans can be requested separately. |
| Tests and coverage | Clear old measurement, run coverage around pytest with the documented selector and pytest-socket. Use pytest's JUnit XML to fail a run with zero executed tests, including an all-skipped suite. Report line/branch threshold via native coverage config after tests pass. |
| Live vulnerabilities | Export the locked runtime graph for the selected extras without dev groups, the project itself, or hashes. Also export the verification environment graph with its selected groups. Audit both exports with `pip-audit --no-deps --disable-pip -r` and machine-readable results. Record advisories, skipped distributions, provider and time. The release record states audited platforms/extras, dependency groups and unsupported sources. Missing provider data or an unexpectedly skipped package leaves the online gate incomplete. |

### Implemented stage details

The recipe emits `PASS <stage>`, `FAIL <stage> exit=<code>`, `SKIP <subcheck> (<reason>)`, and `NOT EXECUTED <stage>` lines. It uses `uv run --no-sync` after the locked offline sync, clears inherited pytest options, loads only `pytest_socket` plus approved project plugins, and passes `--disable-socket`. Evidence is written under ignored `.ai-python/evidence/`; environments and caches stay under ignored `.ai-python/`. The tests stage fails on a nonzero pytest result, a zero/all-skipped JUnit report, or a coverage threshold failure.

The online stage exports the runtime graph with selected extras and the verification graph with the reserved and selected groups, then audits both with `pip-audit --no-deps --disable-pip --strict`. An empty runtime graph is valid for a project without runtime declarations; malformed, skipped, or unavailable provider data fails the adapter check. `lint-imports --config` remains the documented command even though Import Linter 2.17 emits a deprecation warning for that flag.

The implementation uses a fixed recipe sequence and native exit codes. Stop at the first failed required stage, including tool errors or unavailable required data. Emit one status per stage and subcheck when its outcome can differ. **Passed** means the check ran successfully. **Failed** includes a violation, setup or execution error. **Skipped** is an explicit mode or applicability decision with a reason, such as live data in the default mode. **Not executed** means left pending after failure, cancellation, or loss of required evidence. Never infer a passing stage from absent output. Return zero only if every required check passed and the only skips were valid for the mode. Report the failed stage's exit code. CI cancellation or a process kill may omit the footer. Treat absent required entries as not executed.

Record revision, dirty-tree status and changed paths or a diff fingerprint, policy schema and template revision, interpreter and tool versions, entry command/mode, per-stage outcome and exit code, test and coverage summary, and relevant exception IDs. CI preserves results as redacted logs and approved artifacts. For online audit distinguish the check result from a deterministic claim about an evolving vulnerability database. Local success applies to the recorded revision/worktree and measured scope.

## Semantic review and audit

Review the actual diff against the request, policy and gate evidence. Trace important behavior through call sites, interfaces and tests. Examine maintainability, simplicity, coupling, contracts, scientific correctness where applicable, changes to tests and docs, and dependency decisions. Identify an issue with severity, path, evidence and remedy. For an audit, establish repository scope and assess recurring risks, exceptions, missing evidence and policy suitability across the project. Keep observed violations, recommendations, accepted exceptions, and unknowns distinct. A report names the reviewer, analyzed revision, inspected files, commands actually run, findings, disposition and remaining gaps. Maintainers resolve findings, exceptions, and acceptance under [approval rules](skills.md#approvals-and-exceptions).

## Acceptance cases

Implement with pytest in temporary Git repositories, tagged local Copier sources, and small fixtures. Use the pinned native tools and stage-specific assertions. A negative fixture starts from a passing baseline, applies one mutation, asserts the intended stage/diagnostic plus nonzero exit, and proves restoration where useful. Mock no tools in tests claiming their real enforcement. Use a patched provider fixture for deterministic advisory result handling, then a distinct online smoke check for service integration. Use no AI models.

| Case | Required positive and negative evidence | Covers |
| --- | --- | --- |
| A01 | Render valid baseline and combined profile answers. Reject unknown key/type/enum, unsafe paths, empty profile/doc/test scope, bad names, and unresolvable config with no promotion. Assert schema and native ownership checks. | MVP-01, 04, 06, 07 |
| A02 | Library + CLI + Scientific enables the CLI and NumPy recommendation. Backend + Desktop fails unresolved and passes with an explicit architecture choice. A stricter level preserves explicit overrides and post-seed changes. Exercise one unsupported project layout or capability conflict. | MVP-04, 05, 06 |
| A03 | A Standard starter imports, builds, installs, and passes all applicable gates. A CLI starter runs, including invalid input behavior. Install/run its package without development or kit dependencies. | MVP-01, 07, 11 |
| A04 | Change formatting, add a lint violation, then separately trigger configured Ruff complexity, suppression-code, and security rules. Assert stage and diagnostic. Change relevant mypy config and fixture annotations to exercise default and strict checking, implicit optional, unused ignore, redundant cast and explicit `Any`. | MVP-06, 07 |
| A05 | Remove mandatory docs from public declarations, private and custom scope categories including a property and a test. Exercise async, exports, exclusion of unselected objects and nonempty text. An applicable formatting rule fails. Wrong structured argument names fail for Google, NumPy and Sphinx. A missing lint plugin fails. Structured docs with mixed annotations pass under permissive typing when signatures agree. PEP 257 and allowed summary outcomes report the applicable scope. | MVP-06 |
| A06 | For each style, exercise the positive and negative edges given in the policy reference including transitive forbiddance and cycle detection. Flat package is an intentional skip. Claiming flat when mapped qualifying sibling modules exist fails validation. | MVP-05 |
| A07 | Runtime and development `stdlib-only` accept empty scopes and a correct scoped exception. Reject required and optional direct dependencies including marker-disabled ones, prohibited dev group entries, misuse of reserved verification group, an expired/mismatched exception, and unresolved include. Test a runtime missing, unused, transitive and dev-only import with deptry against controlled manifests. | MVP-05, 08 |
| A08 | Default discovers unit + regression, excludes specialized markers, and runs newly selected isolated categories. A Python socket creation attempt fails without dialing a network endpoint. Fixture changes verify selected coverage mode and threshold and fail on empty or all-skipped selection, below threshold and insufficient branch coverage. | MVP-06 |
| A09 | Fail a stale or missing lock without rewriting it. Detect a synthetic test-only Gitleaks match while respecting ignored cache paths. Verify default live-security skip, injected fixture advisory clean/fail/unavailable/unsupported outcomes, a pinned real tool export and a live smoke check outside the deterministic suite. | MVP-07, 09 |
| A10 | Adopt into an existing package with root docs, instructions, native config and other-kit paths. Assert source/tests byte-for-byte and root instruction text retained. Refuse dirty/colliding/symlink cases and expose native config conflicts. An approved scoped legacy baseline passes its permitted findings while fresh violations fail. | MVP-02, 08 |
| A11 | Update between two local tags. Assert user source, root instructions/CI, native settings and owner policy unchanged by Copier. Inspect refreshed answers and changed managed content. Surface deliberate overlap/reject and show rollback of all changes with the Git checkpoint. Reject incompatible schema before acceptance. | MVP-03, 11 |
| A12 | Run the documented command locally and from the CI workflow with matching pins, inputs and gate outcomes. Assert nonzero, failed stage, later not-executed stage and valid skips for a known failure. Missing executable or configuration fails. Verify read-only token, no model calls, and protected review documented. | MVP-09, 10, 11 |
| A13 | Validate every shipped skill with the pinned standard validator. Invalid YAML, missing description and name/directory mismatch fail. Verify manifest commit/path references, expected files, notices and static content hashes offline. Review instructions and license separately. | MVP-08 |
| A14 | Refuse missing required metadata, invalid scope or dates, duplicate exceptions, expired entries and malformed approval references. Human review verifies approval authenticity and rejects a self-approved or stale content identity even if the record is valid. | MVP-08 |

## Enforcement map

**D** means deterministic, **S** semantic review, **H** human approval, and **Hybrid** a combination. A case covers the enforceable portion only.

| Requirement | Class | Limit or companion evidence |
| --- | --- | --- |
| MVP-01 configuration and usable initialization | D | A01–A03 |
| MVP-02 adoption, merge and baseline | Hybrid | A10 plus review of merge and baseline scope |
| MVP-03 update, rollback and supported customization | Hybrid | A11 plus review of lineage, conflicts and migrations |
| MVP-04 profile and override rules | D | A01–A02 |
| MVP-05 architecture and dependencies | Hybrid | A06–A07 plus semantic suitability, runtime coupling and dependency review |
| MVP-06 typing and docstrings | Hybrid | A04–A05 plus semantic public scope, cast justification, accuracy and detail |
| MVP-06 contract, testing and scientific quality | Hybrid | A08 plus independently justified oracles, assumptions, tolerances, isolation and regression review |
| MVP-07 repository, maintainability and security | Hybrid | A04 and A09 plus semantic code quality and external audit coverage and freshness |
| MVP-08 skill structure and provenance | Hybrid | A13 plus content and license review |
| MVP-08 guardrails and semantic review | S | Review the actual diff and evidence using the [skills contract](skills.md) |
| MVP-08 exceptions and final acceptance | H | A07 and A14 validate shape and exact matching. Maintainer review authenticates the authorization. |
| MVP-09 unified verification and truthful evidence | Hybrid | A12 plus evidence review |
| MVP-10 model-free acceptance | D | A01–A14 run repeatably with injected inputs where needed |
| MVP-11 standard packaging, reproducibility and portability | Hybrid | A03, A11 and A12 plus supported-platform matrix and pilot evidence |
