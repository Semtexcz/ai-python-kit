# Architecture

Copy this proposal to the existing project documentation and replace the map with actual modules, or point `[architecture].reference` in `.ai-python/policy.toml` at an existing boundary document.

## Selected style

Record `modular`, `layered`, `hexagonal`, or `custom`, the intended dependency direction, and why the boundary is proportionate to the project.

## Module map

List the production packages and modules, the allowed direction, and any composition root. Map existing modules rather than inventing new ones.

## Static contracts

Name the Import Linter contracts in `.ai-python/config/importlinter.ini`: layers, forbidden imports, independence, protected modules, or acyclic siblings. Include at least one meaningful contract unless the package is intentionally flat.

## Flat decision

If `graph = "flat"`, record why no internal boundary is intended and confirm that the package has at most one immediate importable production child.
