# Bootstrap review

{% if creation_mode == 'init' %}
This directory is the initialization proposal checklist. The rendered project is complete and project-owned from the first Git checkpoint.

## Review before promotion

1. Confirm `display_name`, `distribution_name`, `package`, `python_version`, profiles, quality, architecture, and docstring choices in `.copier-answers.ai-python-kit.yml` and `.ai-python/policy.toml`.
2. Confirm `[architecture].style` and `graph` match the actual package layout. `flat` is valid only with at most one immediate importable child and a recorded reason in `docs/architecture.md`.
3. Review `pyproject.toml`, `uv.lock`, `.python-version`, `.ai-python/config/`, source, tests, `AGENTS.md`, the root `justfile`, and CI.
4. Run the policy-only check:

   ```sh
   just --justfile .ai-python/kit/justfile --working-directory . validate
   ```

5. Generate and commit the lock, sync, and run the full check:

   ```sh
   uv lock
   uv sync --group ai-python-kit
   just --justfile .ai-python/kit/justfile --working-directory . check
   ```

6. Promote the complete staging directory to the new destination on the same filesystem. Do not merge it into a nonempty directory.

Promotion moves the whole directory, so source, tests, policy, native config, and lineage stay together.
{% else %}
This directory is the adoption proposal. The project keeps its existing source, tests, instructions, CI, and manifest.

## Review before integration

1. Confirm names, profiles, quality, architecture, source root, test root, and docstring choices.
2. Run the read-only adoption preflight from the project root, using the adapter from this proposal:

   ```sh
   python /path/to/proposal/.ai-python/kit/adapter/ai_python_policy.py adoption-preflight .
   ```

   Stop on a dirty worktree, an existing `.ai-python` namespace, an existing answers file, or a symlink collision.
3. Compare the proposal with the existing project:

   ```sh
   diff -ru .ai-python /path/to/project/.ai-python
   ```

4. Copy only the kit-owned namespace and lineage file after review: `.ai-python/kit/`, `.ai-python/config/`, `.ai-python/policy.toml`, and `.copier-answers.ai-python-kit.yml`. Preserve other kit namespaces such as `.ai-docs/`.
5. Merge the root integration changes individually from `adopt/`:
   - append the routing block from `adopt/AGENTS-snippet.md` to the existing instructions;
   - add the `adopt/justfile` alias or let the consumer task runner call the same command;
   - adapt `adopt/ci.yml` to the existing CI and pin the same tool versions;
   - create or update `docs/architecture.md` from `adopt/architecture.md` or point `[architecture].reference` at an existing document;
   - add the reserved `ai-python-kit` group and native config ownership to the existing manifest after review.
6. Establish the baseline through approved exceptions or scoped native configuration. Keep active gates for unaffected code. Mark any gate without a stable baseline as pending rather than passed.
7. Run the same check locally and on a pilot CI branch before marking adoption complete.

Existing source and tests are never rewritten by the overlay. Configuration conflicts are explicit merge decisions.
{% endif %}
