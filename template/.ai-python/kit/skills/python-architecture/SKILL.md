---
name: python-architecture
description: Select or assess proportionate Python module boundaries, dependency direction, and static import contracts. Use when adding a component, choosing modular, layered, hexagonal, or custom structure, deciding between flat and contract mode, or fixing architecture contract failures.
---

# Python architecture

Keep the architecture proportional. A boundary needs a current behavior or maintenance reason, not a speculative layer.

## Selection

1. Read `[architecture]` in `.ai-python/policy.toml` and the reference document it names.
2. Map the actual modules. Do not invent modules to satisfy a label.
3. Choose `modular` for independent cohesive components, `layered` for an explicit presentation/application/domain direction, `hexagonal` for an independent domain with ports and adapters, or `custom` for a documented project-specific boundary.
4. Use `graph = "flat"` only when no internal boundary is intended and the package has at most one immediate importable production child excluding `__init__.py`. Record the reason in the reference.
5. Otherwise use `contracts` and at least one meaningful Import Linter contract.

## Contracts

Edit `.ai-python/config/importlinter.ini` and keep the root package aligned with policy. Use `layers`, `forbidden`, `independence`, `protected`, or `acyclic_siblings` as appropriate. Preserve the intended direction of existing modules.

Run the architecture stage through the unified check. Add both positive and negative fixtures when changing a contract: a valid edge must pass, and a direct or transitive forbidden edge must fail. For flat mode, verify that a second importable sibling makes policy validation fail rather than silently skipping the contract.

## Review

Inspect runtime imports, callbacks, dependency injection, and configuration-based coupling alongside the static graph. Reuse shared behavior. Prefer composition when it keeps behavior simpler. Avoid abstractions that only serve a hypothetical future.

## Example

Positive: domain code imports a port interface; the adapter implements it; the composition root wires the concrete adapter; the forbidden contract rejects a domain import of the adapter.

Negative: adding empty `domain/` and `infrastructure/` packages to a small script, or deleting a contract because a new import violates its direction.
