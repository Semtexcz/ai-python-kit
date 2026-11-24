# Project lifecycle

Operational procedures for initialization, adoption, updates, and rollback. The [MVP architecture](mvp.md#lifecycle) defines the contract; this page records the commands and review points for the implemented overlay.

## Prerequisites

- Linux, Git, and Python 3.11 or newer. Python 3.12 is the reference interpreter.
- Copier 9.19.1, uv 0.13.9, just 1.59.0, and Gitleaks 8.30.1. See [toolchain](toolchain.md).
- A clean Git checkpoint for adoption and update work.

The template requires no Copier tasks, migrations, custom Jinja extensions, or trust flag.

## Initialize

Render into staging outside the target:

```sh
copier copy --vcs-ref v0.1.0 https://github.com/Semtexcz/ai-python-kit STAGING
```

No release tag is created by M1/M2. Replace `v0.1.0` with the reviewed tag supplied by the maintainer. A local checkout works for development:

```sh
copier copy --defaults /path/to/ai-python-kit STAGING
```

Review the staged answers and seed before promotion:

```sh
cd STAGING
just --justfile .ai-python/kit/justfile --working-directory . validate
```

`validate` uses the pinned interpreter and standard library only. It rejects blank names, unsafe paths, empty profiles or test categories, unresolved architecture choices, missing native files, duplicate configuration authority, and invalid exception records. It does not install project dependencies or modify tracked files.

Then complete the proposal:

```sh
uv lock
uv sync --group ai-python-kit
just --justfile .ai-python/kit/justfile --working-directory . check
```

Review `.ai-python/kit/bootstrap/README.md`, `.copier-answers.ai-python-kit.yml`, `pyproject.toml`, `.python-version`, `.ai-python/policy.toml`, `.ai-python/config/`, source, tests, `AGENTS.md`, the root `justfile`, and CI. Promote the complete staging directory to a new destination on the same filesystem. Do not merge it into a nonempty directory. Commit the result as the first project checkpoint.

## Adopt

Start from a clean Git checkpoint on an adoption branch. Render an adoption proposal to scratch:

```sh
copier copy --defaults -d creation_mode=adopt \
  -d display_name="Existing Project" -d distribution_name="existing-project" \
  -d package=existing_project --vcs-ref v0.1.0 \
  https://github.com/Semtexcz/ai-python-kit ADOPTION-SCRATCH
```

Run the read-only preflight from the project root, using the adapter from the scratch proposal:

```sh
python ADOPTION-SCRATCH/.ai-python/kit/adapter/ai_python_policy.py adoption-preflight .
```

The preflight refuses a dirty worktree, an existing `.ai-python` namespace or answers file, and symlink collisions. It does not copy files.

Compare the proposal and resolve conflicts before integration:

```sh
diff -ru .ai-python ADOPTION-SCRATCH/.ai-python
diff -u AGENTS.md ADOPTION-SCRATCH/.ai-python/kit/bootstrap/adopt/AGENTS-snippet.md
```

Integrate only the reserved overlay:

- Copy `.ai-python/kit/`, `.ai-python/config/`, `.ai-python/policy.toml`, and `.copier-answers.ai-python-kit.yml`.
- Preserve source, tests, README, root instructions, CI, and other kit namespaces such as `.ai-docs/`.
- Append the routing block from `bootstrap/adopt/AGENTS-snippet.md` to existing instructions.
- Add the root alias from `bootstrap/adopt/justfile` or call the same command from the consumer task runner.
- Adapt `bootstrap/adopt/ci.yml` to the existing workflow and keep the same pins.
- Create `docs/architecture.md` from `bootstrap/adopt/architecture.md` or point `[architecture].reference` at an existing document.
- Add the reserved `ai-python-kit` group and explicit native configuration ownership to `pyproject.toml` in a separately reviewed change.
- Preflight duplicate root Ruff, mypy, Flake8, pytest, coverage, Import Linter, and Gitleaks configuration. Redirect consumers to `.ai-python/config/` or the kit entry point before activation.

Adoption never rewrites existing source or tests. Configuration conflicts are explicit merge decisions.

### Existing technical debt

Record a narrow baseline instead of weakening the whole gate:

- Add `[[exceptions]]` records with the original finding, owner, tracking reference, current threshold or scope, expiry, and human approval. See [exceptions](#exceptions).
- Put native suppressions in the native config or the exact source line and point the record at them.
- Keep active gates for unaffected code.
- If a gate has no stable baseline, leave its full enforcement pending and mark the affected acceptance criteria unsatisfied. Do not report adoption complete.

Run the check locally and on a pilot CI branch before marking adoption complete.

## Update

Use one active installation. Require a clean Git checkpoint, reviewed release notes, a validated template source and lineage, and a compatible policy schema.

```sh
copier update --answers-file .copier-answers.ai-python-kit.yml \
  --vcs-ref v0.2.0 --conflict rej --skip-answered
```

Then inspect:

```sh
git status --short
git diff
find . -name '*.rej' -print
```

Copier manages the overlay and answers. Project-owned source, tests, README, root instructions, CI, and native project choices stay outside the managed overlay. Treat overlap in a managed file as an explicit maintainer merge. A `.rej` file or conflict marker stops acceptance. Review optional seed changes as suggestions and apply native setting or dependency migrations explicitly.

An incompatible policy schema, changed reserved path, stale policy/gate combination, or incomplete merge stops acceptance. Run the same `check` used locally and in CI before merge.

## Rollback

Abandon the update branch, or revert the update commit as a unit. That restores the managed overlay, lineage, and any explicit config or lock change together. Do not revert individual shared files, because that leaves lineage and policy out of sync.

For a promotion that has not been committed, remove the new directory. For an initialized project, the first Git checkpoint is the rollback target.

## Exceptions

An exception is valid only with a stable unique `id`, exact `rule`, narrow `target`, `reason`, accountable `owner`, human `approved_by`, ISO `approved_on` and `expires_on` dates, and `approval_ref`. Expired records fail the applicable gate.

```toml
[[exceptions]]
id = "legacy-import-001"
rule = "importlinter"
target = "example.legacy -> example.adapters"
reason = "Legacy boundary tracked by ADR-004; remove after the adapter split."
owner = "platform-team"
approved_by = "maintainer-name"
approved_on = "2026-11-24"
expires_on = "2027-03-31"
approval_ref = "https://example.invalid/decisions/1234"
```

Structural validation checks shape, matching, duplicates, and dates. It cannot authenticate the approver or prove that the approval covers the final content.

## Safety rules

- Stage outside the target and promote a complete directory on the same filesystem.
- Do not overwrite a nonempty destination.
- Do not use arbitrary Copier tasks or automatic migrations.
- Do not merge managed and project-owned files blindly.
- Do not treat a clean Copier exit as proof that conflicts were resolved.
- Do not claim adoption or update completion without the unified check on the recorded revision.
