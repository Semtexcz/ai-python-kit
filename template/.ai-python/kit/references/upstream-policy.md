# Upstream skill policy

The kit ships one reviewed upstream skill and links three others by pinned revision. The inventory is `.ai-python/kit/upstream-skills.toml`; it records repository, path, commit, version, license, notice location, distribution mode, profiles, purpose, incompatibilities, local changes, and SHA-256 hashes for included files.

## Precedence

1. Project-owned `AGENTS.md` and `.ai-python/policy.toml`.
2. Kit workflow skills and references in this directory.
3. Reviewed upstream recommendations.

If upstream advice conflicts with project policy, project policy wins. Do not run upstream installers, migration commands, or scripts automatically. Do not fetch upstream content during ordinary verification or skill activation.

## Vendored material

`skills/modern-python/` is an unmodified Trail of Bits `modern-python` snapshot under CC BY-SA 4.0. Its `LICENSE` and `NOTICE.md` stay with the files. The generic recommendations for `ty`, `prek`, `uv add`, and migration do not override this project's mypy configuration, approved dependency process, pinned release, or explicit migration authorization.

## Referenced material

`python-pytest` v1.0.0, `python-best-practices` v1.5.0, and `python-async-best-practices` v1.0.0 by Nathan Gage are pinned references only. The repository declares MIT but does not provide a copyright and permission notice suitable for redistribution, so the kit does not ship their content. Read them from the pinned upstream URLs when network access and project policy allow. This project's markers, socket policy, dependency approvals, and baseline remain authoritative.

## Updates

To update, inspect a specific commit on a change branch, compare the exact directory and referenced files, review content and license, resolve policy conflicts, update hashes and notices, validate metadata with the pinned `skills-ref` tool, and record human approval. Consumers receive the change through a reviewed kit update.
