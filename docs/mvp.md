# MVP architecture and lifecycle

Implementation contract for v0.1.0. [Project intent](../PROJECT_INTENT.md) establishes direction. The [implementation plan](implementation-plan.md) establishes sequence and exit evidence.

## Requirements

| ID | Required outcome | Contract |
| --- | --- | --- |
| MVP-01 | A pinned Copier release can initialize a functional Python project. | [Initialize](#initialize) |
| MVP-02 | Adoption preserves existing code and instructions and supports incremental baseline cleanup. | [Adopt](#adopt) |
| MVP-03 | Updates preserve supported customization and expose conflicts with a rollback path. | [Update](#update) |
| MVP-04 | Profiles and quality levels compose predictably. Explicit policies and conflicts are visible. | [Configuration](#configuration) |
| MVP-05 | Projects can specify architecture and runtime/development dependency policies. | [Engineering policies](policies.md) |
| MVP-06 | Projects can specify typing, mandatory docstrings, and isolation and coverage policies. | [Engineering policies](policies.md) |
| MVP-07 | Verification covers repository consistency, maintainability, and security proportionately. | [Verification](verification.md) |
| MVP-08 | Portable skills, project guardrails, semantic review, and exception governance guide agents. | [Agent Skills](skills.md) |
| MVP-09 | People, agents, and CI use one verification entry point and produce explicit outcomes. | [Verification](verification.md) |
| MVP-10 | Positive and negative acceptance tests run without model calls. | [Acceptance cases](verification.md#acceptance-cases) |
| MVP-11 | Projects remain portable, reproducible, and independent within the supported baseline. | [Compatibility](#compatibility) |

## Configuration

### File ownership

Copier renders a namespaced overlay. A reversible staging procedure integrates it into the project. Each concern has one source for the effective project state.

| Path | Authoritative ownership |
| --- | --- |
| `.copier-answers.ai-python-kit.yml` | Copier lineage, including template source/revision and original scaffold selections. Creation inputs are historical after promotion of the seed. |
| `.ai-python/kit/` | Template-owned recipes, adapter, reference text, canonical skills, bootstrap proposals, and CI/pin examples. Apply changes through reviewed Copier updates. |
| `.ai-python/policy.toml` | Project-owned schema version, selected profiles, quality preset used, layout, and engineering choices without a native configuration owner. Exact enums and native mapping appear in [Engineering policies](policies.md). |
| `.ai-python/config/` | Project-owned native Ruff, mypy, Flake8/pydoclint, Import Linter, Gitleaks, and pytest/coverage settings. Docstring format comes from policy. Recipes select native paths explicitly. |
| `pyproject.toml`, `uv.lock`, `.python-version` | Project-owned identity, package/build/dependency declarations, and Python selection. uv owns lock generation. Existing compatible build backends remain selected by the project. |
| Root `AGENTS.md`, README, CI, product source, and tests | Project-owned. Add one agent routing block and one workflow on approval. Updates leave these outside the managed overlay. |

The kit invokes native configuration explicitly. Its paths under `.ai-python/config/` are `ruff.toml`, `mypy.ini`, `flake8.ini`, `importlinter.ini`, `gitleaks.toml`, `pytest.ini`, and `coverage.ini`. deptry reads `[tool.deptry]` from the root manifest. Existing native configs can be moved or extended during adoption. Preflight lists duplicate root sections, files, flags, and CI checks. Redirect consumers and CI that enforce the same Python concern to the selected config or the kit entry point before activation. Separate workflows may retain settings for distinct scopes. The kit recipe and CI reference policy and native config. Agent instructions link to them.

The root policy keys are `schema = 1`, `profiles` (unique nonempty array of `library`, `cli`, `scientific`, `backend`, `desktop`, `automation`, `data-processing`), and `quality` (`minimal`, `standard`, `strict`). The `project` table has `package` (dotted import identifier for one installed root package), `source` (nonempty array of repository-relative production directories or files), `tests` (nonempty array of relative directories), `verify_groups` and `verify_extras` (arrays of existing uv names, initially empty). Kit verification always includes the reserved `ai-python-kit` dependency group. Reject missing or incompatible group and extra combinations. Other tables are specified with their consumers in [Engineering policies](policies.md). A small read-only adapter validates known keys, types, unique selections, real in-repository paths, policy assertions without a native checker, and the existence of the selected files and declarations. Use native validation where a tool owns the value. Use direct native flags for policy-driven arguments. Keep the adapter internal and pass dynamic arguments as argument lists.

### Profiles and quality

Copier asks for a display name, distribution name, import package, Python baseline, creation mode (`init` or `adopt`), a quality level, and independent profile flags. Independent booleans avoid templating a custom multiselect interface. Init defaults are Python 3.12, Library, and Standard. In adopt mode the maintainer records existing names, paths, and compatibility. Blank or ambiguous names and selections fail before promotion. The seed is materialized into project-owned files through explicit review.

| Profile | Contributions at seed time |
| --- | --- |
| Library | Base importable package, public API policy, and behavior tests. |
| CLI | An `argparse` console entry point on init, exit-code contracts, and command-level tests. |
| Scientific computing | NumPy docstring recommendation, numerical and units guidance, and reference-test checklist. |
| Backend/API | Layered architecture recommendation and process, database, and network boundary guidance. Framework selection stays with the project. |
| Desktop application | Hexagonal recommendation and presentation/event-loop guidance. Toolkit selection stays with the project. |
| Automation | Explicit I/O, configuration, and idempotence guidance. CLI can be added independently. |
| Data processing | Schema, validation, and transformation guidance. Uses the same policy switches and guidance mechanism as other profiles. |

Profiles are additive when they contribute distinct values or identical recommendations. Begin with base defaults, then quality defaults, then the union of profile recommendations, then explicit project values. Different recommendations for the same field are an error until the field is set explicitly. Quality presets fill defaults only. They never revise effective native policy or project edits after promotion. For a preset/profile change, stage fresh proposals and review the resulting changes to the owned files. Special recommendations above are a finite seed table, not a rules language.

A Library + CLI + Scientific project receives a console entry, NumPy docstrings, and the standard base package. Backend + Desktop requires explicit `architecture.style` because its recommendations disagree. The Copier answers `architecture_style` and `docstring_format` take `auto` or a supported explicit value. An unresolved auto choice fails validation. All profile labels can coexist after resolution in one package. Multiple packages/workspaces, two conflicting build/runtime selections, unsupported interpreter/platform requirements, missing architecture mappings, and capability requirements incompatible with dependency policy stop the affected workflow. No profile automatically adds an application or scientific runtime dependency.

| Level | Typing seed | Maintainability seed | Coverage seed | Docstring seed |
| --- | --- | --- | --- | --- |
| Minimal | Check untyped bodies, permit missing annotations | Ruff cyclomatic maximum 15 | Line coverage 60% | Public, summary |
| Standard | Typed definitions in production, typed bodies | Cyclomatic maximum 12, maximum 7 arguments | Branch coverage 80% | Public, standard |
| Strict | Standard plus mypy strict and explicit `Any` diagnostics | Cyclomatic maximum 10, maximum 5 arguments | Branch coverage 90% | All production categories, public detailed and private standard |

For all levels use Google format and English by default, isolated pytest, modular architecture where feasible, balanced runtime dependencies, and reuse-first development dependencies. Scope and policy details remain editable as described in the [policy reference](policies.md). An ordinary violation is a check failure. A scoped exception requires [maintainer approval](skills.md#approvals-and-exceptions).

## Lifecycle

### Initialize

1. Install the published release's exact Copier, uv, just, and Gitleaks versions. Fetch a pinned Copier source/tag. Use the same tag for any comparison. Render with `copier copy --vcs-ref TAG SOURCE STAGING` outside the target. The overlay requires no Copier tasks, migrations, custom Jinja extensions, or trust flag.
2. Validate the staged answers and render. Review the initialization proposal under `.ai-python/kit/bootstrap/`, including package source, tests, manifest, policy, native config, Python pin, and root integration snippets. Prepare the full project in staging with the selected proposals, managed namespace and answers. Promote the complete directory to a new destination on the same filesystem. Use the received source/tag in the lineage and open an initial Git checkpoint. Missing files, existing destination entries, invalid settings, or path collisions fail before promotion.
3. Generate and commit `uv.lock` with the pinned uv. Sync the verification environment and run the [verification command](verification.md). The starter exposes a small documented pure function and behavior tests. Modular seeds put it in `core.py` and add `cli.py` when CLI is selected. Layered and hexagonal seeds place the same behavior behind their documented module boundaries and ship matching static contracts. A custom seed requires an explicit project-supplied module map and contracts in staging before promotion. Selecting CLI adds a runnable console entry. Other profiles contribute policy and guidance and leave framework setup to the project. The project owns promoted source and test seeds from the first checkpoint.

### Adopt

1. Start from a clean Git checkpoint on an adoption branch. Check reserved paths and parents for tracked, untracked, ignored, or symlink collisions. Working only in scratch and on the adoption branch, inspect package/build/lock layout, dependencies, tool configs, policy and exceptions, skill names, agent instructions, and CI. Record compatibility and each proposed shared-file change.
2. Render the overlay to scratch with adopt mode. Compare proposals with existing files and resolve collisions before integration. Copy only the reserved overlay paths after review. Apply individual changes for policy/native config, uv verification group, agent routing, and CI. Preserve root instruction text and source/test contents. Adopt existing installable single-root projects through uv, retaining the build backend. Migrate dynamic/legacy dependency metadata to static PEP 621 in a separately reviewed change before activation when required. If the project already has a kit installation, use the update workflow.
3. Establish a baseline using the same target gates. A maintainer can authorize narrowly scoped native baseline entries, path exclusions, or an initial coverage threshold supported by measured coverage. Retain active gates for unaffected code. Where a native gate lacks a stable baseline, leave that gate's full enforcement pending and mark the affected acceptance criteria unsatisfied until activation. Evidence records original finding, owner, tracking reference, current threshold/scope, and expiry. Use [exception governance](skills.md#approvals-and-exceptions). Pilot on CI before marking adoption complete.

### Update

Use one active installation. Require a clean Git checkpoint on a throwaway or update branch, reviewed release notes, validated template source and lineage, and compatible policy schema. Use `copier update --answers-file .copier-answers.ai-python-kit.yml --vcs-ref TAG --conflict rej --skip-answered` from the root with the pinned Copier version. Inspect Git status and diff and look for reject files and conflict markers. Copier manages the overlay and answers only. Treat overlap in managed files as an explicit maintainer merge; keep supported customization in project-owned files. Review optional seed changes as suggestions and apply native setting or dependency migrations explicitly. An unsupported older/newer schema, changed reserved paths, stale policy/gate combination, or incomplete merge stops acceptance. Run the same verification and lifecycle checks before merge. Roll back by abandoning the update branch or reverting the update commit as a unit, including the lineage and any explicit config/lock changes.

## Compatibility

- Baseline is an installable single-package project with static PEP 621 dependencies and a Git checkout. Python 3.11 is the minimum, with 3.12 as the reference verification interpreter for newly generated projects. CI runs the same pinned interpreter as local verification. Support additional versions and platforms only after a project supplies evidence. v0.1.0 release acceptance targets Linux. Keep app/package code and native config portable where practical.
- Use PEP 517/518 build metadata, `uv_build` for generated projects, and PEP 735 development groups. Commit exact tool pins (Copier, uv, just, Gitleaks, action commit SHAs) and the verification lock. Use SemVer tags for the template and a separate policy schema integer. An incompatible policy change requires a new schema version and documented review/upgrade instructions. Record the tested matrix at release.
- A project installs, builds, and runs using normal Python packaging. If the kit is removed, project code and native configs remain with the project. No kit, model, sibling project, or template server is required to run application code. Kit updates and cold dependency installation need their declared sources.
