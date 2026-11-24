# Kit-managed files

This directory is owned by the AI Python Kit and changes through reviewed Copier updates.

- `justfile` is the unified verification recipe.
- `adapter/ai_python_policy.py` is the narrow read-only policy adapter.
- `references/` contains shared policy, review, evidence, exception, and upstream guidance.
- `skills/` contains the canonical Agent Skills.
- `bootstrap/` contains initialization and adoption review material.
- `upstream-skills.toml` records upstream provenance and file hashes.

Do not edit kit-managed files for project-specific behavior. Use `.ai-python/policy.toml`, `.ai-python/config/`, `AGENTS.md`, source, tests, and CI for project-owned choices.

## Commands

```sh
just --justfile .ai-python/kit/justfile --working-directory . validate
just --justfile .ai-python/kit/justfile --working-directory . check
just --justfile .ai-python/kit/justfile --working-directory . check online
```

The default check is offline and deterministic. `check online` adds live dependency vulnerability data. See `references/evidence.md` for the reporting contract.
