# Project intent

## North Star

A maintainer can hand a Python change to any coding agent and use the resulting code, review, and verification evidence to make a sound acceptance decision.

Agents routinely know Python engineering practices yet apply them unevenly across changes. Maintainers need a way to state project policy once, make the routine checks repeatable, and direct human attention to decisions that need judgment. The kit serves maintainers starting or improving Python libraries, tools, and applications, plus the people and agents contributing to them.

## Principles

- Reuse maintained standards and tools first. Compose native configurations before adding code.
- Keep architecture proportional to the project. Favor correctness, clarity, and maintainability over numeric compliance.
- Put each project policy in one authoritative place. Version policy, inputs, and verification tools.
- Use deterministic checks where feasible. Require review for behavior, design, and evidence that tools cannot judge.
- Keep skills portable and load detail on demand. Core requirements apply to every agent.
- Keep generated projects independently usable. Start with the smallest release that solves initialization, adoption, updates, and consistent verification.

## Success at v0.1.0

A new project passes the same verification criteria locally and in CI using a pinned toolchain. A maintainer can adopt the kit without refactoring the entire project or losing code and instructions, then apply an update with local customizations intact or an explicit conflict. Positive and negative fixtures expose gate failures. Acceptance evidence identifies the revision, checks run, findings, and authorized exceptions.

## Scope and boundaries

The kit owns Python engineering policy, Python checks, and task-specific Python skills. [ai-devkit](https://github.com/Semtexcz/ai-devkit) owns general software delivery workflows and cross-language tooling. [ai-project-planner](https://github.com/Semtexcz/ai-project-planner) owns planning and execution management records. [ai-docs-kit](https://github.com/Semtexcz/ai-docs-kit) owns cross-project documentation standards and workflows. A project may combine them by explicitly integrating their entry points and respecting their file ownership.

The first release has no custom CLI, rule or lint framework, audit engine, dependency or skill manager, hosted service, shared runtime framework, model evaluation or benchmarking, or advanced duplicate-code, mutation, performance, or public API compatibility infrastructure. The [MVP specification](docs/mvp.md) defines the supported workflows.
