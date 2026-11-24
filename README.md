# AI Python Kit

AI Python Kit is a toolkit for maintainers and coding agents who want consistent engineering quality in new and existing Python projects. It combines project-owned policy, a Copier overlay, existing verification tools, portable Agent Skills, and review based on evidence.

**Status** · M1/M2 implementation candidate. The overlay, policy adapter, unified check, lifecycle procedures, six Agent Skills, and deterministic tests are implemented. M3 independent acceptance and release preparation are not started.

The kit supports project initialization, adoption, and tagged updates with Copier. Composable profiles guide engineering choices. The local and CI workflow runs the same checks, and maintainers retain authority over policy exceptions and acceptance.

## Start here

| Document | Purpose |
| --- | --- |
| [Project intent](PROJECT_INTENT.md) | Purpose, success criteria, and ecosystem boundaries |
| [Agent instructions](AGENTS.md) | Repository rules and required reading |
| [MVP architecture and lifecycle](docs/mvp.md) | Requirements, configuration ownership, profiles, and workflows |
| [Project lifecycle](docs/lifecycle.md) | Initialize, adopt, update, conflict, and rollback procedures |
| [Engineering policies](docs/policies.md) | Architecture, dependencies, typing, documentation, and testing |
| [Verification and acceptance](docs/verification.md) | Commands, review evidence, and acceptance cases |
| [Agent Skills](docs/skills.md) | Discovery, guardrails, and upstream provenance |
| [Toolchain evidence](docs/toolchain.md) | Pinned versions, licenses, probes, and limitations |
| [Upstream research and decisions](docs/upstream.md) | Candidate evaluations and reuse opportunities |
| [Implementation plan](docs/implementation-plan.md) | M0–M3 scope and exit criteria |
| [M0 report](docs/m0-report.md) | Readiness verdict, traceability, and open risks |
| [M1/M2 report](docs/m1-m2-report.md) | Implementation, traceability, evidence, and M3 handoff |

## Repository layout

- `copier.yml` and `template/` produce the namespaced overlay.
- `tests/` verifies the template, adapter, lifecycle, skills, and real-tool gates.
- `docs/` holds the contract, operational guidance, and evidence.
- The kit itself uses `pyproject.toml`, `uv.lock`, and the root `justfile` for maintainer checks.

Related work includes [ai-devkit](https://github.com/Semtexcz/ai-devkit), [ai-project-planner](https://github.com/Semtexcz/ai-project-planner), and [ai-docs-kit](https://github.com/Semtexcz/ai-docs-kit). The kit follows the open [Agent Skills specification](https://agentskills.io/specification).
