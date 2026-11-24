# Upstream research and decisions

Source review completed on 2026-11-24. This records selection evidence from upstream documentation, package metadata, and repository files. M0 used read-only inspection. The integration pins and tested matrix are M1/M3 outputs. No upstream script was run.

## Consequential decisions

| Decision | Selection and rationale |
| --- | --- |
| D01 · Generation and ownership | Use Copier with a reserved overlay namespace, staged seed promotion, and project-owned native configs. Native tagged updates preserve a defined ownership boundary. Adoption uses explicit merges for existing files. |
| D02 · Enforcement | Use native tools and a narrow adapter for constraints without a native consumer, particularly direct dependency modes, policy reconciliation, and custom docstring presence. Retain semantic review and verified human approval for judgment and authority. |
| D03 · Skills | Keep one portable source per skill, review pinned upstream materials and license terms, and expose host discovery as an opt-in. Project policy applies before upstream advice. |

## Standards

| Source | Applicable guidance |
| --- | --- |
| [Scientific Python Development Guide](https://learn.scientific-python.org/development/) | Reuse packaging, tests, automation, and scientific development practices. Apply them selectively to a project of the relevant size and profile. |
| [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) and [PEP index](https://peps.python.org/) | Use Google for the default structured docstring format. Use relevant PEPs for language and packaging conventions. Subset lint rules by the kit's policy. |
| [PEP 8](https://peps.python.org/pep-0008/), [PEP 20](https://peps.python.org/pep-0020/), [PEP 257](https://peps.python.org/pep-0257/) | Use Python idioms, readable conventions, simple design, and general docstring conventions. Ruff and semantic review apply the relevant parts. |
| [Python Packaging User Guide](https://packaging.python.org/), [typing specification](https://typing.python.org/), [NumPy docstring conventions](https://numpydoc.readthedocs.io/en/latest/format.html), and [Sphinx fields](https://www.sphinx-doc.org/en/master/usage/domains/python.html#info-field-lists) | Adopt standard manifests and package builds, cite typing semantics, and support three structured formats plus PEP 257 conventions. |
| [Agent Skills specification](https://agentskills.io/specification), [AGENTS.md](https://agents.md/), and [Diátaxis](https://diataxis.fr/) | Use portable instructions, lean workflow entries, scoped references, and reader-oriented documentation. |

Standards remain upstream references with no redistributed standards text.

## Selected tools

Python development tools resolve through the project lock. Release instructions pin standalone tools and runtime. Tools install from upstream sources with their distribution licenses and notices. M1 records release-specific license and notice evidence for included files. Recent docs/releases and accessible repositories supported selection. A published release still needs the pinned smoke matrix.

| Candidate | Suitability, maintenance evidence and remaining cost |
| --- | --- |
| [Copier](https://github.com/copier-org/copier), MIT | Maintained 9.x line. Native questions, validators, Jinja, answers and tagged updates cover basic lifecycle. Use one namespace and no task execution. Scratch promotion and update conflict fixtures establish safety. [Configuration](https://copier.readthedocs.io/en/stable/configuring/) · [Updates](https://copier.readthedocs.io/en/stable/updating/) |
| [uv and uv_build](https://github.com/astral-sh/uv), MIT or Apache-2.0 | Maintained project tooling with dependency groups, locking and sync. Build standard distributions. Use one package environment and lock; keep existing compatible build backends on adoption. Requires pinning uv and checking offline cache behavior. [Lock/sync](https://docs.astral.sh/uv/concepts/projects/sync/) · [Build](https://docs.astral.sh/uv/concepts/projects/build/) |
| [Ruff](https://github.com/astral-sh/ruff), MIT | Maintained, single lint and format binary. Native TOML supports explicit rule and scope selection. Replaces separate formatter, pydocstyle and complexity tools for covered rules. Public presence rules cannot express all private/custom categories. [Rules](https://docs.astral.sh/ruff/rules/) · [Settings](https://docs.astral.sh/ruff/settings/) |
| [mypy](https://github.com/python/mypy), MIT with component notices | Maintained, mature controls over untyped bodies, `Any`, implicit optional, casts and ignores. Explicit config and locked stubs if needed. Run one type checker. Maintain scope and strictness through project config. [Config reference](https://mypy.readthedocs.io/en/stable/config_file.html) |
| [pytest](https://docs.pytest.org/), MIT, [coverage.py](https://coverage.readthedocs.io/), Apache-2.0, and [pytest-socket](https://github.com/miketheman/pytest-socket), MIT | Maintained suites and coverage docs, with coverage.py 7.17.5 visible in the review. pytest fixtures/markers, coverage branch and threshold settings, and explicit socket plugin serve distinct roles. pytest-socket has a narrow Python process boundary and requires explicit activation and validation. |
| [pydoclint](https://github.com/jsh9/pydoclint) and [Flake8](https://github.com/PyCQA/flake8), MIT | Maintained signature checker for Google, NumPy and Sphinx. The standalone checker lacks project-wide code selection. Run the plugin under Flake8 to select signature diagnostics without coupling them to annotation strictness. Flake8 hosts this plugin only. Ruff remains responsible for lint and format. Verify parser behavior per style. [Native and plugin modes](https://github.com/jsh9/pydoclint#34-native-tool-or-flake8-plugin) · [Diagnostic selection](https://flake8.pycqa.org/en/latest/user/violations.html) |
| [Import Linter](https://github.com/import-linter/import-linter), BSD-2-Clause | Maintained native import contracts, including forbidden, layers and acyclic siblings. Use installed package and local configuration. Statically visible import paths are the verified scope. Rebuild no graph. [Contracts](https://import-linter.readthedocs.io/en/stable/) · [Acyclic siblings](https://import-linter.readthedocs.io/en/stable/contract_types/acyclic_siblings/) |
| [deptry](https://deptry.com/), MIT, and [packaging](https://packaging.pypa.io/), Apache-2.0 or BSD-2-Clause | Maintained config-driven import checks and standard requirement parser. deptry detects missing, unused, transitive and dev-only imports in scoped production code. Direct declaration policy uses packaging and native TOML. Group discovery and first-party mappings need pinned feature tests. |
| [Gitleaks](https://github.com/gitleaks/gitleaks), MIT, and [pip-audit](https://github.com/pypa/pip-audit), Apache-2.0 | Maintained scanners with distinct native outputs and update costs. Redact worktree secret findings; scope the filesystem check. Audit a pinned graph export against live advisories without re-resolving. Validate known fixtures and unavailable/unsupported outcomes. |
| [just](https://github.com/casey/just), CC0-1.0, and [GitHub Actions](https://docs.github.com/en/actions), hosted service | Maintained lightweight command runner and CI integration. Explicit project root and fixed ordered recipe. GitHub permissions and exact action pins are required for the reference workflow. The same CLI works locally or on other CI. |
| [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref), Apache-2.0 | Reference validator with source and validation CLI in the maintained standards repo. Pin a specific revision for maintainer-only metadata checks. Review content and provenance independently. |

## Alternatives and optional tools

| Candidate | Finding and disposition |
| --- | --- |
| [Scientific Python Cookie](https://github.com/scientific-python/cookie), BSD-3-Clause, and [Trail of Bits Cookiecutter Python](https://github.com/trailofbits/cookiecutter-python), Apache-2.0 | Both accessible. Reuse layout and guidance patterns from active Scientific Python materials and modern Python baseline choices from Trail of Bits. Cookiecutter-shaped generation would duplicate scaffolding and gives no selected tagged-update workflow. No template code is selected for import. |
| [ty](https://docs.astral.sh/ty/) | Maintained upstream and aligned with uv/Ruff, with per-rule configuration. mypy's established typing-policy controls and existing maintainer configs meet the MVP criteria. No second checker or performance comparison. |
| [pytest-randomly](https://github.com/pytest-dev/pytest-randomly), [Hypothesis](https://hypothesis.readthedocs.io/), and [time-machine](https://time-machine.readthedocs.io/) | Accessible, focused optional tools. Random order with recorded seeds can expose coupling, Hypothesis finds counterexamples, and time-machine controls clock inputs. They add configuration, dependencies or reproducibility considerations. Default to pytest fixtures and explicit inputs. Allow individually approved opt-ins. |
| [repo-review](https://github.com/scientific-python/repo-review) and [sp-repo-review](https://pypi.org/project/sp-repo-review/) | Active public sources for repository and Scientific Python checklist checks. The old standalone sp-repo-review GitHub path was unavailable through web read; the maintainer's [guide](https://learn.scientific-python.org/development/guides/repo-review/) and [framework README](https://github.com/scientific-python/repo-review) link the maintained package. Their policy overlaps owned lock, layout and config checks and adds opinionated checks outside the MVP. |
| [Grimp](https://github.com/python-grimp/grimp) | The old seddonym path redirects here. Import Linter already supplies graph contracts. Direct graph integration would add support burden with no required gap. |
| [pydocstyle](https://github.com/PyCQA/pydocstyle), [Radon](https://radon.readthedocs.io/) and [Vulture](https://github.com/jendrikseipp/vulture) | Ruff covers selected formatting and complexity signals. Vulture provides wider static dead-code warnings with false positives in dynamic projects. Start with Ruff and focused review. No parallel gates. |
| [Task](https://taskfile.dev/) and [pre-commit](https://pre-commit.com/) | Maintained options. Task's task graph/configuration adds no needed capability for a fixed command sequence. pre-commit is appropriate as an opt-in caller of the recipe. A hook would create an additional setup path and cannot establish merge authority. |
| [TestMu AI pytest-skill](https://github.com/LambdaTest/agent-skills/blob/main/pytest-skill/SKILL.md) | Accessible entry declares MIT and covers pytest mechanics and examples. Nathan Gage's testing skill addresses the identified test quality and reproducibility gaps more directly. No redistribution. |
| [Trail of Bits property-based testing and related skills](https://github.com/trailofbits/skills) | Active collection, with the property-testing guidance useful as specialist reference. Leave wider static analysis and security workflows outside the default installation. Ruff, native scanners, and review cover the specified MVP scope. |
| [OpenAI skill-creation guidance](https://github.com/openai/skills/tree/main/skills/.system/skill-creator) | Use the concise entry, trigger-focused descriptions and progressive disclosure guidance as a reference. Preserve the open format and manual discovery, with no infrastructure dependency or copied scripts. [Current hosted guidance](https://learn.chatgpt.com/docs/build-skills) |

The selected external skills, pinned revisions, license constraints, and update policy live in the [provenance specification](skills.md#proposed-upstream-provenance).

## Maintainer ecosystem

The three sibling projects were inspected from accessible local files and their remote README through GitHub. Direct web requests for their repository landing pages missed cache, so they were supplemented with connector reads. Historical sources were inspected through GitHub file contents. Preserve the boundaries in [Project intent](../PROJECT_INTENT.md).

| Repository and inspected artifact | Reuse opportunity |
| --- | --- |
| [ai-devkit](https://github.com/Semtexcz/ai-devkit) · AGENTS.md, Copier config, generated-project ownership and old template comparison | Adopt reuse-first, locked uv tasks, explicit tool/file ownership, validation-only checks, and two-tag update evidence. If integrated, let the consumer's general task runner call the Python kit check. |
| [ai-project-planner](https://github.com/Semtexcz/ai-project-planner) · AGENTS.md, milestone asset, governance reference | Use outcome, dependencies, accountable reviewer, and explicit exit evidence in the plan. Reuse content-specific human approval and reject self-authorization. Leave planner records and status with the planner. |
| [ai-docs-kit](https://github.com/Semtexcz/ai-docs-kit) · AGENTS.md, documentation architecture and file-ownership decision | Adopt namespaced updates, seed-once ownership principles, relative navigation, focused English documents and traceable evidence. Kit-specific docstring policy belongs here. |
| [_ai_python_project_template](https://github.com/Semtexcz/_ai_python_project_template) · README, AGENTS.md and copier.yml | Reuse compact src/tests layout, uv and CI pattern, and profile defaults. Historical Typer, FastAPI and TUI bundles would impose runtime dependencies, so this release leaves their selection to the project. |
| [_ai_project_template](https://github.com/Semtexcz/_ai_project_template) · README, [pinned architecture](https://github.com/Semtexcz/_ai_project_template/blob/d035235c09cf057665cdc526acffa231724b9614/docs/template-architecture.md), and ai-devkit's comparison | Reuse independent configuration dimensions, state ownership and evidence-backed acceptance. The managed workflow, Make orchestration and full-stack profiles serve a broader scope. |
| [_ai_architecture_project_template](https://github.com/Semtexcz/_ai_architecture_project_template) · README | Reuse its service-boundary and contract framing. Product coordination, Docker orchestration and multi-repository scaffolding remain separate. |

The reference projects inform design. This milestone copies no source or template from them. Check file-level licenses before any literal reuse.

## Remaining validation

M1 verifies Copier's seed/update behavior, pytest plugin isolation and marker commands, contract matching, pydoclint modes, deptry group behavior, tool and interpreter pins, and audit export/exclusion handling. M2 verifies full vendored scope and notices. M3 tests positive/negative cases, provider smoke and independent pilot adoption. See the [implementation plan](implementation-plan.md) for the disposition of any failed native claim.
