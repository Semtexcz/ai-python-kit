"""Read-only policy adapter for the AI Python Kit verification workflow.

The adapter covers constraints without a native consumer: policy shape and
cross-references, direct dependency modes, docstring presence, architecture
mode selection, pytest category selection, and result interpretation for JUnit
and pip-audit reports. Native tools keep their own configuration and exit codes.

The module never writes project files. It runs on the pinned interpreter and
uses only the standard library except for the ``dependencies`` subcommand,
which uses the installed ``packaging`` requirement parser.
"""

from __future__ import annotations

import argparse
import ast
import configparser
import json
import re
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

POLICY_PATH = Path(".ai-python/policy.toml")
CONFIG_DIR = Path(".ai-python/config")
RESERVED_GROUP = "ai-python-kit"
EXPECTED_VERIFICATION_TOOLS = frozenset(
    {
        "coverage",
        "deptry",
        "flake8",
        "import-linter",
        "mypy",
        "packaging",
        "pip-audit",
        "pydoclint",
        "pytest",
        "pytest-socket",
        "ruff",
    }
)
PROFILES = frozenset(
    {
        "library",
        "cli",
        "scientific",
        "backend",
        "desktop",
        "automation",
        "data-processing",
    }
)
QUALITY_LEVELS = frozenset({"minimal", "standard", "strict"})
ARCHITECTURE_STYLES = frozenset({"modular", "layered", "hexagonal", "custom"})
GRAPH_MODES = frozenset({"contracts", "flat"})
DEPENDENCY_MODES = frozenset({"reuse-first", "balanced", "minimal", "stdlib-only"})
ANNOTATION_SCOPES = frozenset({"public", "production", "custom"})
DOCSTRING_FORMATS = frozenset({"google", "numpy", "sphinx", "pep257"})
DOCSTRING_SCOPES = frozenset({"public", "all", "custom"})
DOCSTRING_DETAILS = frozenset({"summary", "standard", "detailed"})
DOCSTRING_CATEGORIES = frozenset(
    {"modules", "classes", "functions", "methods", "properties", "tests"}
)
TEST_CATEGORIES = frozenset({"unit", "integration", "regression", "property", "end_to_end"})
SPECIAL_TEST_MARKERS = ("external", "stochastic", "performance")
POLICY_KEYS = frozenset(
    {
        "schema",
        "profiles",
        "quality",
        "project",
        "architecture",
        "dependencies",
        "typing",
        "docstrings",
        "testing",
        "review",
        "exceptions",
    }
)
EXCEPTION_KEYS = frozenset(
    {
        "id",
        "rule",
        "target",
        "reason",
        "owner",
        "approved_by",
        "approved_on",
        "expires_on",
        "approval_ref",
    }
)
NATIVE_CONFIG_FILES = (
    "ruff.toml",
    "mypy.ini",
    "flake8.ini",
    "importlinter.ini",
    "gitleaks.toml",
    "pytest.ini",
    "coverage.ini",
)
DUPLICATE_CONFIG_FILES = (
    "ruff.toml",
    ".ruff.toml",
    "mypy.ini",
    ".flake8",
    ".coveragerc",
    ".gitleaks.toml",
    "importlinter.ini",
    ".importlinter",
    "pytest.ini",
    "tox.ini",
)
PACKAGE_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*)*$")
VERIFICATION_COMMAND = "just --justfile .ai-python/kit/justfile"


class AdapterError(Exception):
    """Raised when a required input cannot be read or parsed."""


@dataclass(frozen=True)
class Policy:
    """Parsed policy plus the raw TOML data used by individual checks."""

    root: Path
    data: dict[str, Any]
    today: date

    @property
    def project(self) -> dict[str, Any]:
        """Return the project table."""
        return _table(self.data, "project")

    @property
    def exceptions(self) -> list[dict[str, Any]]:
        """Return structurally valid exception records available for matching."""
        records = self.data.get("exceptions", [])
        if not isinstance(records, list):
            return []
        return [record for record in records if isinstance(record, dict)]


def _table(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    return value if isinstance(value, dict) else {}


def _load_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError as exc:
        raise AdapterError(f"missing file: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise AdapterError(f"invalid TOML in {path}: {exc}") from exc


def load_policy(root: Path) -> Policy:
    """Load the project policy from the given project root.

    Args:
        root: Repository root containing ``.ai-python/policy.toml``.

    Returns:
        Parsed policy data.

    Raises:
        AdapterError: If the policy file is missing or malformed.
    """
    return Policy(root=root, data=_load_toml(root / POLICY_PATH), today=date.today())


def _is_relative_path(value: str) -> bool:
    path = Path(value)
    return bool(value.strip()) and not path.is_absolute() and ".." not in path.parts


def _repo_path(root: Path, value: str) -> Path | None:
    if not _is_relative_path(value):
        return None
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _add(problems: list[str], message: str) -> None:
    problems.append(message)


def _require_table(data: dict[str, Any], key: str, problems: list[str]) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        _add(problems, f"policy: missing [{key}] table")
        return {}
    return value


def _require_keys(
    table: dict[str, Any], name: str, keys: Iterable[str], problems: list[str]
) -> None:
    for key in keys:
        if key not in table:
            _add(problems, f"policy: [{name}] is missing '{key}'")


def _enum(
    table: dict[str, Any],
    name: str,
    key: str,
    choices: frozenset[str],
    problems: list[str],
) -> None:
    value = table.get(key)
    if not isinstance(value, str) or value not in choices:
        _add(
            problems,
            f"policy: [{name}].{key} must be one of {', '.join(sorted(choices))}",
        )


def _string_list(
    table: dict[str, Any],
    name: str,
    key: str,
    problems: list[str],
    *,
    allow_empty: bool = False,
) -> list[str]:
    value = table.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        _add(problems, f"policy: [{name}].{key} must be an array of strings")
        return []
    if not allow_empty and not value:
        _add(problems, f"policy: [{name}].{key} must not be empty")
    if len(set(value)) != len(value):
        _add(problems, f"policy: [{name}].{key} must not contain duplicates")
    return value


def _parse_date(value: Any, label: str, problems: list[str]) -> date | None:
    if not isinstance(value, str):
        _add(problems, f"exception {label}: expected an ISO date string")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        _add(problems, f"exception {label}: invalid ISO date '{value}'")
        return None


def _validate_exception_record(
    record: dict[str, Any], label: str, policy: Policy, problems: list[str]
) -> None:
    missing = EXCEPTION_KEYS - set(record)
    unknown = set(record) - EXCEPTION_KEYS
    if missing:
        _add(problems, f"exception {label}: missing {', '.join(sorted(missing))}")
    if unknown:
        _add(problems, f"exception {label}: unknown {', '.join(sorted(unknown))}")
    for key in ("id", "rule", "target", "reason", "owner", "approved_by", "approval_ref"):
        value = record.get(key)
        if not isinstance(value, str) or not value.strip():
            _add(problems, f"exception {label}: '{key}' must be a non-empty string")
    rule = record.get("rule")
    if isinstance(rule, str) and re.search(r"\s", rule):
        _add(problems, f"exception {label}: rule must not contain whitespace")
    approved = _parse_date(record.get("approved_on"), f"{label}.approved_on", problems)
    expires = _parse_date(record.get("expires_on"), f"{label}.expires_on", problems)
    if approved and expires and approved > expires:
        _add(problems, f"exception {label}: approved_on is after expires_on")
    if expires and expires < policy.today:
        _add(
            problems,
            f"exception {label}: expired on {expires.isoformat()} "
            f"(current UTC date {policy.today.isoformat()})",
        )


def _validate_exceptions(policy: Policy, problems: list[str]) -> None:
    records = policy.data.get("exceptions", [])
    if records is None:
        return
    if not isinstance(records, list):
        _add(problems, "policy: exceptions must be an array of tables")
        return
    seen: set[str] = set()
    for index, record in enumerate(records, start=1):
        label = f"#{index}"
        if not isinstance(record, dict):
            _add(problems, f"exception {label}: expected a table")
            continue
        _validate_exception_record(record, label, policy, problems)
        identifier = record.get("id")
        if isinstance(identifier, str):
            if identifier in seen:
                _add(problems, f"exception {label}: duplicate id '{identifier}'")
            seen.add(identifier)


def _valid_exceptions(policy: Policy) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for record in policy.exceptions:
        rule = record.get("rule")
        target = record.get("target")
        expires = record.get("expires_on")
        if not isinstance(rule, str) or not isinstance(target, str):
            continue
        if not isinstance(expires, str):
            continue
        try:
            expired = date.fromisoformat(expires) < policy.today
        except ValueError:
            expired = True
        if not expired:
            result[(rule, target)] = record
    return result


def _known_config_conflicts(root: Path, problems: list[str]) -> None:
    for name in DUPLICATE_CONFIG_FILES:
        path = root / name
        if path.exists():
            _add(
                problems,
                f"duplicate native configuration '{name}'; redirect it to "
                f"{CONFIG_DIR / name} or remove it",
            )
    pyproject_path = root / "pyproject.toml"
    if pyproject_path.exists():
        pyproject = _load_toml(pyproject_path)
        tool = _table(pyproject, "tool")
        for owner, keys in (
            ("ruff", ("ruff",)),
            ("mypy", ("mypy",)),
            ("pytest", ("pytest",)),
            ("coverage", ("coverage",)),
        ):
            section = tool.get(owner)
            if isinstance(section, dict) and section:
                _add(
                    problems,
                    f"duplicate [tool.{owner}] in pyproject.toml; move it to "
                    f".ai-python/config/{keys[0]}.ini or the documented native path",
                )
    setup_cfg = root / "setup.cfg"
    if setup_cfg.exists():
        parser = configparser.ConfigParser()
        parser.read(setup_cfg)
        for section in ("mypy", "flake8", "pytest", "coverage:run", "coverage:report"):
            if parser.has_section(section):
                _add(
                    problems,
                    f"duplicate [{section}] in setup.cfg; redirect it to the kit config",
                )


def _package_root(
    root: Path, source_paths: Sequence[str], package: str, problems: list[str]
) -> Path | None:
    package_rel = Path(*package.split("."))
    candidates: list[Path] = []
    for source in source_paths:
        base = root / source
        nested = base / package_rel
        if nested.is_dir():
            candidates.append(nested)
        elif base.is_dir() and base.name == package.split(".")[0]:
            candidates.append(base)
    unique = sorted({path.resolve() for path in candidates})
    if len(unique) > 1:
        _add(problems, f"policy: package '{package}' is ambiguous across source roots")
        return None
    return unique[0] if unique else None


def _immediate_children(package_root: Path) -> list[str]:
    children: list[str] = []
    for child in sorted(package_root.iterdir()):
        if child.name == "__init__.py" or child.name.startswith("."):
            continue
        if child.is_file() and child.suffix == ".py":
            children.append(child.stem)
        elif child.is_dir() and (child / "__init__.py").is_file():
            children.append(child.name)
    return children


def _validate_architecture(
    root: Path,
    policy: Policy,
    project: dict[str, Any],
    source_paths: Sequence[str],
    problems: list[str],
) -> None:
    architecture = _require_table(policy.data, "architecture", problems)
    if not architecture:
        return
    _require_keys(architecture, "architecture", ("style", "reference", "graph"), problems)
    _enum(architecture, "architecture", "style", ARCHITECTURE_STYLES, problems)
    _enum(architecture, "architecture", "graph", GRAPH_MODES, problems)
    reference = architecture.get("reference")
    if isinstance(reference, str) and reference.strip():
        reference_path = _repo_path(root, reference)
        if reference_path is None or not reference_path.is_file():
            _add(problems, f"policy: architecture.reference '{reference}' is not a file")
        elif not reference_path.read_text(encoding="utf-8").strip():
            _add(problems, f"policy: architecture.reference '{reference}' is empty")
    else:
        _add(problems, "policy: [architecture].reference must be a non-empty path")

    importlinter = root / CONFIG_DIR / "importlinter.ini"
    if not importlinter.is_file():
        _add(problems, f"policy: missing native contract file {importlinter}")
        return
    parser = configparser.ConfigParser()
    parser.read(importlinter)
    contracts = [
        section for section in parser.sections() if section.startswith("importlinter:contract:")
    ]
    root_package = parser.get("importlinter", "root_package", fallback="")
    package = project.get("package")
    if root_package != package:
        _add(
            problems,
            f"{importlinter}: root_package '{root_package}' does not match "
            f"policy package '{package}'",
        )
    graph = architecture.get("graph")
    if graph == "contracts" and not contracts:
        _add(problems, f"{importlinter}: contract mode requires at least one contract")
    if architecture.get("style") == "custom" and graph != "contracts":
        _add(problems, 'policy: custom architecture requires graph = "contracts"')
    if graph == "flat":
        package_root = _package_root(root, source_paths, str(package), problems)
        if package_root is not None:
            children = _immediate_children(package_root)
            if len(children) > 1:
                _add(
                    problems,
                    "policy: flat graph is invalid because the package has "
                    f"{len(children)} immediate importable children ({', '.join(children)}); "
                    'add contracts and set graph = "contracts"',
                )


def _validate_project(root: Path, policy: Policy, problems: list[str]) -> dict[str, Any]:
    project = _require_table(policy.data, "project", problems)
    if not project:
        return project
    _require_keys(
        project,
        "project",
        ("package", "source", "tests", "verify_groups", "verify_extras"),
        problems,
    )
    package = project.get("package")
    if not isinstance(package, str) or not PACKAGE_PATTERN.fullmatch(package):
        _add(problems, "policy: [project].package must be a dotted Python identifier")
        package = ""
    source_paths = _string_list(project, "project", "source", problems)
    test_paths = _string_list(project, "project", "tests", problems)
    for value in source_paths + test_paths:
        resolved = _repo_path(root, value)
        if resolved is None or not resolved.exists():
            _add(problems, f"policy: path '{value}' is not a real repository path")
    if package and source_paths:
        package_root = _package_root(root, source_paths, package, problems)
        if package_root is None:
            _add(
                problems,
                f"policy: package '{package}' was not found under {source_paths}",
            )

    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.is_file():
        _add(problems, "policy: missing project pyproject.toml for dependency checks")
        return project
    pyproject = _load_toml(pyproject_path)
    project_table = _table(pyproject, "project")
    groups = _table(pyproject, "dependency-groups")
    extras = _table(project_table, "optional-dependencies")
    _validate_verify_targets(project, groups, extras, problems)
    _validate_reserved_group(groups, problems)
    return project


def _validate_verify_targets(
    project: dict[str, Any],
    groups: dict[str, Any],
    extras: dict[str, Any],
    problems: list[str],
) -> None:
    verify_groups = _string_list(project, "project", "verify_groups", problems, allow_empty=True)
    verify_extras = _string_list(project, "project", "verify_extras", problems, allow_empty=True)
    if RESERVED_GROUP in verify_groups:
        _add(
            problems,
            f"policy: verify_groups must not list the reserved '{RESERVED_GROUP}' group",
        )
    for group in verify_groups:
        if group != RESERVED_GROUP and group not in groups:
            _add(problems, f"policy: verify_groups references unknown group '{group}'")
    for extra in verify_extras:
        if extra not in extras:
            _add(problems, f"policy: verify_extras references unknown extra '{extra}'")


def _validate_reserved_group(groups: dict[str, Any], problems: list[str]) -> None:
    if RESERVED_GROUP not in groups:
        _add(problems, f"policy: pyproject.toml is missing [{RESERVED_GROUP}] group")
        return
    entries = groups[RESERVED_GROUP]
    if not isinstance(entries, list) or not all(isinstance(entry, str) for entry in entries):
        _add(problems, f"policy: reserved group '{RESERVED_GROUP}' must be a string list")
        return
    names = [_normalized_name(re.split(r"[<>=!~ ;\[]", entry)[0]) for entry in entries]
    if len(set(names)) != len(names):
        _add(problems, f"policy: reserved group '{RESERVED_GROUP}' has duplicates")
    if set(names) == EXPECTED_VERIFICATION_TOOLS:
        return
    extra_tools = sorted(set(names) - EXPECTED_VERIFICATION_TOOLS)
    missing_tools = sorted(EXPECTED_VERIFICATION_TOOLS - set(names))
    _add(
        problems,
        f"policy: reserved group '{RESERVED_GROUP}' must contain the exact "
        "verification tool set"
        + (f"; unexpected: {', '.join(extra_tools)}" if extra_tools else "")
        + (f"; missing: {', '.join(missing_tools)}" if missing_tools else ""),
    )


def _validate_dependencies_table(policy: Policy, problems: list[str]) -> None:
    dependencies = _require_table(policy.data, "dependencies", problems)
    if not dependencies:
        return
    _enum(dependencies, "dependencies", "runtime", DEPENDENCY_MODES, problems)
    _enum(dependencies, "dependencies", "development", DEPENDENCY_MODES, problems)
    for key in ("approve_runtime_additions", "approve_development_additions"):
        if not isinstance(dependencies.get(key), bool):
            _add(problems, f"policy: [dependencies].{key} must be a boolean")


def _validate_typing_table(policy: Policy, problems: list[str]) -> None:
    typing = _require_table(policy.data, "typing", problems)
    if not typing:
        return
    _enum(typing, "typing", "annotation_scope", ANNOTATION_SCOPES, problems)
    if typing.get("annotation_scope") != "custom":
        return
    reference = typing.get("scope_reference")
    if not isinstance(reference, str) or not reference.strip():
        _add(problems, "policy: custom typing scope requires scope_reference")
        return
    path = _repo_path(policy.root, reference)
    if path is None or not path.is_file():
        _add(problems, f"policy: typing.scope_reference '{reference}' is not a file")


def _validate_docstring_table(policy: Policy, problems: list[str]) -> None:
    docstrings = _require_table(policy.data, "docstrings", problems)
    if not docstrings:
        return
    _enum(docstrings, "docstrings", "format", DOCSTRING_FORMATS, problems)
    _enum(docstrings, "docstrings", "scope", DOCSTRING_SCOPES, problems)
    _enum(docstrings, "docstrings", "public_detail", DOCSTRING_DETAILS, problems)
    _enum(docstrings, "docstrings", "private_detail", DOCSTRING_DETAILS, problems)
    language = docstrings.get("language")
    if not isinstance(language, str) or not language.strip():
        _add(problems, "policy: [docstrings].language must be a non-empty string")
    if docstrings.get("scope") != "custom":
        return
    categories = _string_list(docstrings, "docstrings", "categories", problems)
    unknown = set(categories) - DOCSTRING_CATEGORIES
    if unknown:
        _add(
            problems,
            "policy: [docstrings].categories has unsupported values: " + ", ".join(sorted(unknown)),
        )


def _validate_testing_table(policy: Policy, problems: list[str]) -> None:
    testing = _require_table(policy.data, "testing", problems)
    if not testing:
        return
    categories = _string_list(testing, "testing", "categories", problems)
    unknown = set(categories) - TEST_CATEGORIES
    if unknown:
        _add(
            problems,
            "policy: [testing].categories has unsupported values: " + ", ".join(sorted(unknown)),
        )
    plugins = _string_list(testing, "testing", "plugins", problems, allow_empty=True)
    if not all(plugin.strip() for plugin in plugins):
        _add(problems, "policy: [testing].plugins must not contain blank names")


def _validate_review_table(policy: Policy, problems: list[str]) -> None:
    review = _require_table(policy.data, "review", problems)
    for key in ("function_lines", "module_lines"):
        value = review.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            _add(problems, f"policy: [review].{key} must be a positive integer")


def _validate_engineering_tables(policy: Policy, problems: list[str]) -> None:
    _validate_dependencies_table(policy, problems)
    _validate_typing_table(policy, problems)
    _validate_docstring_table(policy, problems)
    _validate_testing_table(policy, problems)
    _validate_review_table(policy, problems)


def _validate_policy_header(data: dict[str, Any], problems: list[str]) -> None:
    unknown = set(data) - POLICY_KEYS
    if unknown:
        _add(problems, f"policy: unknown keys: {', '.join(sorted(unknown))}")
    if data.get("schema") != 1:
        _add(problems, "policy: schema must be 1")
    profiles = data.get("profiles")
    if not isinstance(profiles, list) or not all(isinstance(profile, str) for profile in profiles):
        _add(problems, "policy: profiles must be an array of strings")
    else:
        if not profiles:
            _add(problems, "policy: profiles must not be empty")
        if len(set(profiles)) != len(profiles):
            _add(problems, "policy: profiles must not contain duplicates")
        unsupported = set(profiles) - PROFILES
        if unsupported:
            _add(
                problems,
                "policy: unsupported profiles: " + ", ".join(sorted(unsupported)),
            )
    if data.get("quality") not in QUALITY_LEVELS:
        _add(problems, "policy: quality must be minimal, standard, or strict")


def _validate_native_references(root: Path, problems: list[str]) -> None:
    for name in NATIVE_CONFIG_FILES:
        path = root / CONFIG_DIR / name
        if not path.is_file():
            _add(problems, f"policy: missing native config {path}")
    agents = root / "AGENTS.md"
    if not agents.is_file():
        _add(problems, "policy: missing root AGENTS.md routing instructions")
    elif VERIFICATION_COMMAND not in agents.read_text(encoding="utf-8"):
        _add(problems, f"policy: AGENTS.md must reference '{VERIFICATION_COMMAND}'")
    if not (root / ".copier-answers.ai-python-kit.yml").is_file():
        _add(problems, "policy: missing .copier-answers.ai-python-kit.yml lineage file")


def validate_policy(policy: Policy) -> list[str]:
    """Validate policy shape, cross-references, native files, and exceptions.

    Args:
        policy: Parsed policy and project root.

    Returns:
        Human-readable problems; an empty list means the policy is valid.
    """
    problems: list[str] = []
    _validate_policy_header(policy.data, problems)
    project = _validate_project(policy.root, policy, problems)
    source_paths = project.get("source")
    resolved_sources = (
        [source for source in source_paths if isinstance(source, str)]
        if isinstance(source_paths, list)
        else []
    )
    _validate_architecture(policy.root, policy, project, resolved_sources, problems)
    _validate_engineering_tables(policy, problems)
    _validate_exceptions(policy, problems)
    _known_config_conflicts(policy.root, problems)
    _validate_native_references(policy.root, problems)
    return problems


def _normalized_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _canonicalize(name: str) -> str:
    from packaging.utils import canonicalize_name

    return canonicalize_name(name)


def _parse_requirements(entries: Any, label: str, problems: list[str]) -> list[tuple[str, str]]:
    from packaging.requirements import InvalidRequirement, Requirement

    parsed: list[tuple[str, str]] = []
    if not isinstance(entries, list):
        _add(problems, f"{label}: expected an array of requirement strings")
        return parsed
    for entry in entries:
        if not isinstance(entry, str):
            _add(problems, f"{label}: requirement entries must be strings")
            continue
        try:
            requirement = Requirement(entry)
        except InvalidRequirement as exc:
            _add(problems, f"{label}: invalid requirement '{entry}': {exc}")
            continue
        parsed.append((_canonicalize(requirement.name), entry))
    return parsed


def check_dependencies(policy: Policy) -> list[str]:
    """Check direct declaration policy independently of deptry import analysis.

    Args:
        policy: Parsed policy and project root.

    Returns:
        Human-readable problems; an empty list means declarations satisfy policy.
    """
    problems: list[str] = []
    pyproject = _load_toml(policy.root / "pyproject.toml")
    project = _table(pyproject, "project")
    dynamic = project.get("dynamic", [])
    if isinstance(dynamic, list) and (
        "dependencies" in dynamic or "optional-dependencies" in dynamic
    ):
        _add(problems, "dependencies: dynamic dependency metadata is not supported")
    runtime = _parse_requirements(project.get("dependencies", []), "runtime", problems)
    extras = _table(project, "optional-dependencies")
    for extra_name, entries in sorted(extras.items()):
        runtime.extend(_parse_requirements(entries, f"runtime extra '{extra_name}'", problems))

    groups = _table(pyproject, "dependency-groups")
    dependency_modes = _table(policy.data, "dependencies")
    development = _collect_development(pyproject, groups, problems)
    approved = _valid_exceptions(policy)
    _check_stdlib_only("runtime", runtime, dependency_modes, approved, problems)
    _check_stdlib_only("development", development, dependency_modes, approved, problems)
    _check_exception_targets(policy, problems)
    return problems


def _collect_development(
    pyproject: dict[str, Any], groups: dict[str, Any], problems: list[str]
) -> list[tuple[str, str]]:
    development: list[tuple[str, str]] = []
    include_targets: list[str] = []
    for group_name, entries in sorted(groups.items()):
        if group_name == RESERVED_GROUP:
            if isinstance(entries, list) and any(isinstance(entry, dict) for entry in entries):
                _add(
                    problems,
                    f"dependencies: reserved group '{RESERVED_GROUP}' must not "
                    "include other groups",
                )
            continue
        if not isinstance(entries, list):
            _add(problems, f"dependencies: group '{group_name}' must be an array")
            continue
        for entry in entries:
            if isinstance(entry, str):
                development.extend(
                    _parse_requirements([entry], f"development group '{group_name}'", problems)
                )
            elif isinstance(entry, dict) and set(entry) == {"include-group"}:
                target = entry.get("include-group")
                if not isinstance(target, str) or target not in groups:
                    _add(
                        problems,
                        f"dependencies: group '{group_name}' includes unresolved group '{target}'",
                    )
                else:
                    include_targets.append(target)
            else:
                _add(
                    problems,
                    f"dependencies: group '{group_name}' has an unsupported entry",
                )
    if RESERVED_GROUP in include_targets:
        _add(
            problems,
            f"dependencies: project groups must not include the reserved '{RESERVED_GROUP}' group",
        )
    tool = _table(pyproject, "tool")
    uv_table = _table(tool, "uv")
    legacy = uv_table.get("dev-dependencies", [])
    development.extend(_parse_requirements(legacy, "legacy tool.uv.dev-dependencies", problems))
    return development


def _check_stdlib_only(
    scope: str,
    declarations: list[tuple[str, str]],
    modes: dict[str, Any],
    approved: dict[tuple[str, str], dict[str, Any]],
    problems: list[str],
) -> None:
    if modes.get(scope) != "stdlib-only":
        return
    rule = f"dependency.{scope}"
    for name, raw in declarations:
        if (rule, name) not in approved:
            _add(
                problems,
                f"{scope} dependency '{name}' from '{raw}' violates stdlib-only "
                "mode and has no exact approved exception",
            )


def _check_exception_targets(policy: Policy, problems: list[str]) -> None:
    for record in policy.exceptions:
        rule = record.get("rule")
        target = record.get("target")
        if (
            rule in {"dependency.runtime", "dependency.development"}
            and isinstance(target, str)
            and target != _canonicalize(target)
        ):
            _add(
                problems,
                f"exception '{record.get('id')}': dependency target '{target}' "
                "must use the normalized package name",
            )


def _is_public_name(name: str) -> bool:
    return not name.startswith("_")


DocNode = ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef


def _has_docstring(node: DocNode) -> bool:
    docstring = ast.get_docstring(node, clean=False)
    return isinstance(docstring, str) and bool(docstring.strip())


def _decorator_name(decorator: ast.expr) -> str:
    if isinstance(decorator, ast.Name):
        return decorator.id
    if isinstance(decorator, ast.Attribute):
        return decorator.attr
    return ""


def _has_decorator(node: ast.FunctionDef | ast.AsyncFunctionDef, name: str) -> bool:
    return any(_decorator_name(item) == name for item in node.decorator_list)


def _property_kind(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    names = {_decorator_name(item) for item in node.decorator_list}
    if "property" in names or "cached_property" in names:
        return "getter"
    if names & {"setter", "getter", "deleter"}:
        return "accessor"
    return ""


@dataclass(frozen=True)
class _DocTarget:
    path: Path
    line: int
    kind: str
    name: str


def _target(path: Path, node: DocNode, kind: str, name: str, missing: list[_DocTarget]) -> None:
    if not _has_docstring(node):
        missing.append(_DocTarget(path, getattr(node, "lineno", 1), kind, name))


def _check_function_group(
    path: Path,
    nodes: Sequence[ast.FunctionDef | ast.AsyncFunctionDef],
    kind: str,
    prefix: str,
    require: bool,
    missing: list[_DocTarget],
) -> None:
    overloads = [node for node in nodes if _has_decorator(node, "overload")]
    if overloads:
        implementations = [node for node in nodes if not _has_decorator(node, "overload")]
        if not implementations:
            return
        nodes = implementations[-1:]
    for node in nodes:
        if require:
            _target(path, node, kind, prefix + node.name, missing)


@dataclass
class _DocContext:
    path: Path
    categories: set[str]
    scope: str
    missing: list[_DocTarget]
    warnings: list[str]


def _check_property_group(
    context: _DocContext,
    class_name: str,
    name: str,
    nodes: Sequence[ast.FunctionDef | ast.AsyncFunctionDef],
    method_public: bool,
) -> None:
    if "properties" not in context.categories:
        return
    getter = next((item for item in nodes if _property_kind(item) == "getter"), None)
    if getter is not None:
        _target(context.path, getter, "property", f"{class_name}.{name}", context.missing)
    elif context.scope in {"all", "custom"} or method_public:
        for item in nodes:
            _target(context.path, item, "property", f"{class_name}.{name}", context.missing)


def _check_method_group(
    context: _DocContext,
    class_name: str,
    name: str,
    nodes: Sequence[ast.FunctionDef | ast.AsyncFunctionDef],
    method_public: bool,
) -> None:
    if "methods" not in context.categories or not (
        context.scope in {"all", "custom"} or method_public
    ):
        return
    if _has_decorator(nodes[0], "overload") and len(nodes) == 1:
        context.warnings.append(f"{context.path}:{nodes[0].lineno}: overload-only method '{name}'")
    _check_function_group(context.path, nodes, "method", f"{class_name}.", True, context.missing)


def _check_class(context: _DocContext, node: ast.ClassDef, *, public: bool) -> None:
    if "classes" in context.categories and (context.scope in {"all", "custom"} or public):
        _target(context.path, node, "class", node.name, context.missing)
    methods: dict[str, list[ast.FunctionDef | ast.AsyncFunctionDef]] = {}
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.setdefault(child.name, []).append(child)
    for name, nodes in sorted(methods.items()):
        method_public = public and _is_public_name(name)
        if context.scope == "public" and not method_public:
            continue
        if _property_kind(nodes[0]):
            _check_property_group(context, node.name, name, nodes, method_public)
        else:
            _check_method_group(context, node.name, name, nodes, method_public)


def _warn_dynamic_all(context: _DocContext, statement: ast.stmt) -> None:
    targets: Sequence[ast.expr]
    value: ast.expr | None
    if isinstance(statement, ast.Assign):
        targets = statement.targets
        value = statement.value
    elif isinstance(statement, ast.AnnAssign):
        targets = [statement.target]
        value = statement.value
    else:
        return
    if any(
        isinstance(target, ast.Name) and target.id == "__all__" for target in targets
    ) and not isinstance(value, (ast.List, ast.Tuple)):
        context.warnings.append(f"{context.path}:{statement.lineno}: dynamic __all__ needs review")


def _check_module_statement(
    context: _DocContext, statement: ast.stmt, *, public_module: bool
) -> None:
    if isinstance(statement, ast.ClassDef):
        public = _is_public_name(statement.name)
        if context.scope == "public" and not public:
            return
        _check_class(context, statement, public=public and public_module)
    elif isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
        public = _is_public_name(statement.name)
        if context.scope == "public" and (not public or not public_module):
            return
        if "functions" not in context.categories or _has_decorator(statement, "overload"):
            return
        _target(context.path, statement, "function", statement.name, context.missing)


def _check_module(
    path: Path,
    relpath: str,
    *,
    scope: str,
    categories: set[str],
    missing: list[_DocTarget],
    warnings: list[str],
) -> None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        missing.append(_DocTarget(path, exc.lineno or 1, "syntax", relpath))
        return
    public_module = all(not part.startswith("_") for part in Path(relpath).parts[:-1]) and (
        not path.stem.startswith("_") or path.name == "__init__.py"
    )
    context = _DocContext(path, categories, scope, missing, warnings)
    if "modules" in categories and (scope in {"all", "custom"} or public_module):
        _target(path, tree, "module", relpath, missing)
    for statement in tree.body:
        _warn_dynamic_all(context, statement)
        _check_module_statement(context, statement, public_module=public_module)


def _python_files(root: Path, paths: Sequence[str]) -> list[Path]:
    files: set[Path] = set()
    skip = {"__pycache__", "build", "dist", ".venv", ".git"}
    for value in paths:
        base = (root / value).resolve()
        if not base.exists():
            continue
        if base.is_file() and base.suffix == ".py":
            files.add(base)
            continue
        for path in base.rglob("*.py"):
            if any(part in skip or part.startswith(".ai-python") for part in path.parts):
                continue
            files.add(path.resolve())
    return sorted(files)


def missing_docstrings(policy: Policy) -> tuple[list[str], list[str]]:
    """Report missing mandatory docstrings and review warnings.

    Args:
        policy: Parsed policy and project root.

    Returns:
        A tuple of failure messages and non-failing review warnings.
    """
    docstrings = _table(policy.data, "docstrings")
    scope = docstrings.get("scope", "public")
    if scope == "public" or scope == "all":
        categories = {"modules", "classes", "functions", "methods", "properties"}
    else:
        categories = set(docstrings.get("categories", []))
    project = _table(policy.data, "project")
    source_paths = project.get("source", [])
    test_paths = project.get("tests", [])
    if not isinstance(source_paths, list):
        source_paths = []
    if not isinstance(test_paths, list):
        test_paths = []
    missing: list[_DocTarget] = []
    warnings: list[str] = []
    for path in _python_files(policy.root, source_paths):
        _check_module(
            path,
            str(path.relative_to(policy.root.resolve())),
            scope=str(scope),
            categories=categories,
            missing=missing,
            warnings=warnings,
        )
    if scope == "custom" and "tests" in categories:
        test_categories = {"modules", "classes", "functions", "methods"}
        for path in _python_files(policy.root, test_paths):
            _check_module(
                path,
                str(path.relative_to(policy.root.resolve())),
                scope="all",
                categories=test_categories,
                missing=missing,
                warnings=warnings,
            )
    failures = [
        f"{item.path.relative_to(policy.root.resolve())}:{item.line}: "
        f"missing {item.kind} docstring for '{item.name}'"
        for item in missing
    ]
    return failures, warnings


def pytest_selector(policy: Policy) -> str:
    """Build the native pytest ``-m`` expression for selected categories.

    Args:
        policy: Parsed policy.

    Returns:
        A pytest marker expression.

    Raises:
        AdapterError: If no test category is selected.
    """
    testing = _table(policy.data, "testing")
    selected = testing.get("categories")
    if not isinstance(selected, list) or not selected:
        raise AdapterError("testing.categories must not be empty")
    categories = [item for item in selected if isinstance(item, str)]
    positive = " or ".join(categories)
    if "unit" in categories:
        excluded = [
            category
            for category in ("integration", "regression", "property", "end_to_end")
            if category not in categories
        ]
        if excluded:
            positive = f"{positive} or (not {' and not '.join(excluded)})"
    negative = " and ".join(f"not {marker}" for marker in SPECIAL_TEST_MARKERS)
    return f"({positive}) and {negative}"


def junit_failures(path: Path) -> list[str]:
    """Fail a run with zero executed tests, including an all-skipped suite.

    Args:
        path: JUnit XML report written by pytest.

    Returns:
        Human-readable problems.
    """
    try:
        tree = ET.parse(path)
    except (OSError, ET.ParseError) as exc:
        return [f"junit: cannot read {path}: {exc}"]
    cases = tree.getroot().iter("testcase")
    total = 0
    executed = 0
    for case in cases:
        total += 1
        if case.find("skipped") is None:
            executed += 1
    if total == 0:
        return ["junit: the selected suite collected no tests"]
    if executed == 0:
        return ["junit: every selected test was skipped; zero tests executed"]
    return []


def audit_failures(path: Path) -> list[str]:
    """Interpret a pip-audit JSON report without performing an audit.

    Args:
        path: JSON report written by pip-audit.

    Returns:
        Human-readable problems.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"audit: cannot read {path}: {exc}"]
    dependencies = payload.get("dependencies")
    if not isinstance(dependencies, list):
        return ["audit: report has no dependencies array; provider data is unavailable"]
    problems: list[str] = []
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            problems.append("audit: malformed dependency record")
            continue
        name = dependency.get("name", "unknown")
        skip_reason = dependency.get("skip_reason")
        if skip_reason:
            problems.append(f"audit: {name} was skipped: {skip_reason}")
        for vulnerability in dependency.get("vulns", []):
            if isinstance(vulnerability, dict):
                problems.append(
                    f"audit: {name} {dependency.get('version', '')} has "
                    f"{vulnerability.get('id', 'an advisory')}"
                )
    return problems


def _git(target: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(target), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def adoption_preflight(target: Path) -> list[str]:
    """Refuse a dirty, colliding, symlinked, or non-Git adoption target.

    Args:
        target: Existing project directory.

    Returns:
        Human-readable problems.
    """
    problems: list[str] = []
    if not target.is_dir():
        return [f"adoption: target '{target}' is not a directory"]
    inside = _git(target, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return [f"adoption: target '{target}' is not a Git worktree"]
    status = _git(target, "status", "--porcelain")
    if status.returncode != 0:
        problems.append(f"adoption: cannot inspect Git status: {status.stderr.strip()}")
    elif status.stdout.strip():
        problems.append("adoption: target worktree is not clean")
    for relative in (".ai-python", ".copier-answers.ai-python-kit.yml"):
        path = target / relative
        if path.is_symlink():
            problems.append(f"adoption: reserved path '{relative}' is a symlink")
        elif path.exists():
            problems.append(f"adoption: reserved path '{relative}' already exists")
    return problems


def _paths(policy: Policy, kind: str) -> list[str]:
    project = _table(policy.data, "project")
    source = project.get("source", [])
    tests = project.get("tests", [])
    if not isinstance(source, list) or not isinstance(tests, list):
        raise AdapterError("project source and tests must be arrays")
    if kind == "source":
        return [item for item in source if isinstance(item, str)]
    if kind == "tests":
        return [item for item in tests if isinstance(item, str)]
    if kind == "package":
        package = str(project.get("package", ""))
        package_rel = Path(*package.split(".")) if package else Path()
        values: list[str] = []
        for item in source:
            if not isinstance(item, str):
                continue
            # A non-root source directory is already the configured production
            # root. For a repository-root source, narrow to the package to avoid
            # type-checking tests and tooling.
            if Path(item) == Path("."):
                nested = package_rel
                values.append(str(nested) if (policy.root / nested).exists() else item)
            else:
                values.append(item)
        return values
    if kind == "docs":
        docstrings = _table(policy.data, "docstrings")
        categories = docstrings.get("categories", [])
        include_tests = (
            docstrings.get("scope") == "custom"
            and isinstance(categories, list)
            and "tests" in categories
        )
        values = [item for item in source if isinstance(item, str)]
        if include_tests:
            values += [item for item in tests if isinstance(item, str)]
        return values
    raise AdapterError(f"unknown path kind: {kind}")


def _sync_args(policy: Policy) -> list[str]:
    project = _table(policy.data, "project")
    groups = project.get("verify_groups", [])
    extras = project.get("verify_extras", [])
    args = ["--group", RESERVED_GROUP]
    if isinstance(groups, list):
        for group in groups:
            if isinstance(group, str) and group != RESERVED_GROUP:
                args.extend(["--group", group])
    if isinstance(extras, list):
        for extra in extras:
            if isinstance(extra, str):
                args.extend(["--extra", extra])
    return args


def _architecture_mode(policy: Policy) -> str:
    architecture = _table(policy.data, "architecture")
    return str(architecture.get("graph", ""))


def _docstring_format(policy: Policy) -> str:
    return str(_table(policy.data, "docstrings").get("format", ""))


def _plugins(policy: Policy) -> list[str]:
    testing = _table(policy.data, "testing")
    plugins = testing.get("plugins", [])
    return [item for item in plugins if isinstance(item, str)] if isinstance(plugins, list) else []


def _export_runtime_args(policy: Policy) -> list[str]:
    project = _table(policy.data, "project")
    extras = project.get("verify_extras", [])
    args: list[str] = []
    if isinstance(extras, list):
        for extra in extras:
            if isinstance(extra, str):
                args.extend(["--extra", extra])
    return args


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only policy adapter for the AI Python Kit.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root (default: current directory).",
    )
    parser.add_argument(
        "--today",
        type=date.fromisoformat,
        default=date.today(),
        help="Override the UTC acceptance date for repeatable fixtures.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate", help="Validate policy and native references.")
    subcommands.add_parser("dependencies", help="Check direct dependency policy.")
    subcommands.add_parser("docstrings", help="Check mandatory docstring presence.")
    subcommands.add_parser("pytest-selector", help="Print the pytest marker selector.")
    subcommands.add_parser("architecture-mode", help="Print contracts or flat.")
    subcommands.add_parser("docstring-format", help="Print the selected docstring format.")
    subcommands.add_parser("plugins", help="Print approved pytest plugin import names.")
    subcommands.add_parser("sync-args", help="Print uv sync group and extra arguments.")
    subcommands.add_parser(
        "export-runtime-args", help="Print uv export extra arguments for runtime audit."
    )
    paths = subcommands.add_parser("paths", help="Print configured paths.")
    paths.add_argument("kind", choices=["source", "tests", "docs", "package"])
    junit = subcommands.add_parser("junit-check", help="Check a JUnit XML report.")
    junit.add_argument("path", type=Path)
    audit = subcommands.add_parser("audit-check", help="Interpret a pip-audit JSON report.")
    audit.add_argument("path", type=Path)
    adoption = subcommands.add_parser(
        "adoption-preflight", help="Refuse an unsafe adoption target."
    )
    adoption.add_argument("target", type=Path)
    return parser


REPORT_COMMANDS = frozenset({"junit-check", "audit-check", "adoption-preflight"})
_PRINTERS: dict[str, Callable[[Policy], list[str]]] = {
    "pytest-selector": lambda policy: [pytest_selector(policy)],
    "architecture-mode": lambda policy: [_architecture_mode(policy)],
    "docstring-format": lambda policy: [_docstring_format(policy)],
    "plugins": _plugins,
    "sync-args": _sync_args,
    "export-runtime-args": _export_runtime_args,
}


def _report_command(args: argparse.Namespace, root: Path) -> list[str]:
    if args.command == "junit-check":
        return junit_failures(args.path)
    if args.command == "audit-check":
        return audit_failures(args.path)
    target = args.target if args.target.is_absolute() else root / args.target
    return adoption_preflight(target)


def _policy_lines(args: argparse.Namespace, policy: Policy) -> list[str] | None:
    if args.command == "paths":
        return _paths(policy, args.kind)
    printer = _PRINTERS.get(args.command)
    return printer(policy) if printer is not None else None


def _policy_problems(args: argparse.Namespace, policy: Policy) -> list[str]:
    if args.command == "validate":
        return validate_policy(policy)
    if args.command == "dependencies":
        return check_dependencies(policy)
    if args.command == "docstrings":
        problems, warnings = missing_docstrings(policy)
        for warning in warnings:
            print(f"review: {warning}", file=sys.stderr)
        return problems
    raise AdapterError(f"unknown command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run a read-only adapter subcommand.

    Args:
        argv: Optional argument list. Defaults to ``sys.argv[1:]``.

    Returns:
        ``0`` when the requested check passes and ``1`` otherwise.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command in REPORT_COMMANDS:
            problems = _report_command(args, root)
        else:
            loaded = load_policy(root)
            policy = Policy(root=root, data=loaded.data, today=args.today)
            lines = _policy_lines(args, policy)
            if lines is not None:
                for line in lines:
                    print(line)
                return 0
            problems = _policy_problems(args, policy)
    except AdapterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if problems:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
