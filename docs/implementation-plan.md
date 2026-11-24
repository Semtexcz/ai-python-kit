# Implementation plan

Each milestone has an observable outcome and exit evidence. The maintainer authorizes activation and accepts the result. Work packages have dependencies and evidence without requiring an external planner. Refer to the [requirements](mvp.md#requirements) and [acceptance cases](verification.md#acceptance-cases) for exact scope.

## M0 — Bootstrap and specification

- **Outcome** · A future implementation agent can build the MVP from explicit contracts and scoped choices.
- **Dependencies** · Project brief, workspace inspection, and focused primary-source research.
- **Tasks** · Establish intent and boundaries. Inspect sibling kits and reference templates. Decide tool and ownership model. Specify policy, lifecycle, skills, acceptance evidence, and M1–M3 handoff. Review the artifacts and Git diff.
- **Deliverables** · Project intent, README, agent instructions, linked specifications, this plan, and the [M0 report](m0-report.md).
- **Exit evidence** · Requirements are traceable. Proposed sources, enforcement limits and validation work are explicit. The diff contains specification artifacts only.
- **Non-goals** · Production code, rendered template, finished skills, gate scripts, acceptance implementation, and release.

## M1 — Core template, policy and deterministic tooling

- **Progress (2026-11-24)** · Implemented in the repository: namespaced Copier overlay, profile composition, policy adapter, native configuration, unified recipe, lifecycle procedures, and deterministic tests. Local A01–A12 coverage is recorded in the [M1/M2 report](m1-m2-report.md). Independent M3 acceptance remains open; this is not a release.
- **Outcome** · A pinned release candidate overlay can initialize, adopt and update one supported Python project and run repeatable gates.
- **Dependencies** · M0 contracts and maintainer authorization. Pin and demonstrate tool compatibility before relying on a gate.
- **Tasks**
  1. Verify exact Copier 9.x syntax and render/update behavior, uv build/runtime compatibility, mypy options, Import Linter contract names, deptry group behavior, pydoclint styles/short summaries, and test/shell flags. Select releases compatible with Python 3.11+ and the Linux/Python 3.12 acceptance matrix. Record exact pins, license identifiers, and install sources. Resolve differences in native capability in the spec before claiming coverage.
  2. Implement the namespaced Copier render, bootstrap proposals, profile merge/validation, policy schema and narrowly scoped adapter. Preserve the root and maintain the inventory of project-owned and managed paths.
  3. Wire native configs, verification modes, redacted Gitleaks, pytest-socket, coverage, and online audit. Confirm locked offline replay and same command in local and CI. Update the source and configuration inventories consumed by verification.
  4. Document staged initialize/adopt/update operations, compatibility, and rollback. Run focused real-tool smoke probes with tagged sources and small temporary projects. Preserve evidence for M3.
- **Deliverables** · Versioned template, policy and native config examples, small adapter and recipes, CI example, source/pin inventory, lifecycle instructions, and smoke results.
- **Exit evidence** · Profile conflict and explicit override behave as specified. One new and one existing project run local verification, a mutation fails at an intended stage, and an update preserves project-owned paths or exposes conflict. Record evidence for A01–A12 as it becomes available. M3 performs the full independent acceptance pass.
- **Non-goals** · Finished skills or prompts, app scaffolds and frameworks beyond the baseline/CLI, general config merger, custom rule or CLI framework, and final release.

## M2 — Skills, guardrails and semantic workflows

- **Progress (2026-11-24)** · Implemented: six workflow skills, shared references, root routing and guardrails, pinned upstream inventory, vendored Trail of Bits materials with notice, Nathan Gage references with the license fallback, and metadata/hash tests. Independent content and approval review remains with M3.
- **Outcome** · Model-independent agent guidance routes real changes through adopted policy, verification and human acceptance.
- **Dependencies** · M0 skill and review contracts. Write against the specified paths and interface alongside M1. Validate rendered routing and evidence after M1 stabilizes them. M1 and M2 can run as one authorized implementation pass.
- **Tasks**
  1. Write the six small skills and shared review/evidence references. Supply root routing, host discovery options, manual fallback, and the approval flow with narrowly scoped exception examples.
  2. Review full selected pinned upstream skill snapshots and related references, file-level license, and remaining conflicts. Record hashes/notices and validate metadata via pinned upstream tooling. If the MIT notice for Nathan Gage's testing skill cannot be confirmed, use the pinned reference.
  3. Exercise clean implementation, review and audit evidence envelopes as documentation scenarios. Verify that missing evidence stays visible and that no workflow self-approves. Align generated instructions with the M1 gates, approval ownership, and policy location.
- **Deliverables** · Canonical project-local skills and references, provenance manifest, validation setup for maintainers, root guardrails, and review and audit examples.
- **Exit evidence** · All shipped skills pass metadata validation and provenance checks. Maintainer review finds effective policy precedence and a manual discovery path. Positive and negative scenario walkthroughs demonstrate A13 and A14 boundaries.
- **Non-goals** · Skill manager, host-specific duplicate distribution, model benchmarks, or agent-dependent acceptance tests.

## M3 — Independent acceptance and release preparation

- **Status** · Not started. M1/M2 stop before independent review and release work.
- **Outcome** · The maintainer has independent evidence to accept or remediate v0.1.0.
- **Dependencies** · M1 and M2 exits, one representative pre-existing pilot project, and a reviewer independent of the implementation.
- **Tasks**
  1. Implement and run the full A01–A14 automated suite. Exercise local and CI parity, compatibility pins, skill notices, and redacted evidence. Run the live dependency-service smoke check separately.
  2. Pilot staged adoption and one update in the representative project. Check root policy/instructions, source preservation, ratchet behavior, and failure recovery. Review architecture proportionality, scientific/testing guidance and semantic evidence.
  3. Remediate and rerun failures. Record the tested matrix, remaining limitations, third-party notices, and acceptance report. Prepare release notes, version and rollback guidance for maintainer review.
- **Deliverables** · Acceptance fixtures and results, independent review, pilot evidence, remediation, compatibility/notice records, and release-preparation checklist.
- **Exit evidence** · Mandatory cases meet their stated criteria on the pinned matrix. Required live, semantic, and approval evidence is present. Outstanding blockers remain visible and prevent release approval.
- **Non-goals** · Expanding support to additional platforms or architectures as a side effect, exhaustive permutations, model evaluations, or publishing without distinct authorization.

Plan format borrows observable outcomes, exit criteria, dependencies and evidence ownership from the [maintainer's planning kit](https://github.com/Semtexcz/ai-project-planner).
