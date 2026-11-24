"""Policy and native-reference validation on rendered projects."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.support import ADAPTER_PATH, run


def _replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"missing fixture text: {old}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _validate(project: Path) -> object:
    return run(
        [
            sys.executable,
            ADAPTER_PATH,
            "--root",
            project,
            "--today",
            "2026-11-24",
            "validate",
        ],
        cwd=project,
    )


def _remove_agents(project: Path) -> str:
    (project / "AGENTS.md").unlink()
    return "missing root AGENTS.md"


def _remove_agents_command(project: Path) -> str:
    _replace(project / "AGENTS.md", ".ai-python/kit/justfile", "some other command")
    return "AGENTS.md must reference"


def _remove_native_config(project: Path) -> str:
    (project / ".ai-python/config/coverage.ini").unlink()
    return "missing native config"


def _duplicate_root_ruff(project: Path) -> str:
    (project / "ruff.toml").write_text("line-length = 90\n", encoding="utf-8")
    return "duplicate native configuration 'ruff.toml'"


def _duplicate_tool_mypy(project: Path) -> str:
    with (project / "pyproject.toml").open("a", encoding="utf-8") as handle:
        handle.write("\n[tool.mypy]\nstrict = false\n")
    return "duplicate [tool.mypy]"


def _flat_with_two_children(project: Path) -> str:
    (project / "src/example/extra.py").write_text('"""Extra."""\n', encoding="utf-8")
    return "flat graph is invalid"


def _empty_profiles(project: Path) -> str:
    _replace(project / ".ai-python/policy.toml", 'profiles = ["library"]', "profiles = []")
    return "profiles must not be empty"


def _unknown_key(project: Path) -> str:
    _replace(
        project / ".ai-python/policy.toml",
        "schema = 1",
        "schema = 1\nunknown_key = 1",
    )
    return "unknown keys"


def _bad_source_path(project: Path) -> str:
    _replace(
        project / ".ai-python/policy.toml",
        'source = ["src"]',
        'source = ["../src"]',
    )
    return "not a real repository path"


def _bad_package(project: Path) -> str:
    _replace(project / ".ai-python/policy.toml", 'package = "example"', 'package = "Bad-Package"')
    return "dotted Python identifier"


def _missing_architecture_reference(project: Path) -> str:
    _replace(
        project / ".ai-python/policy.toml",
        'reference = "docs/architecture.md"',
        'reference = "docs/missing.md"',
    )
    return "architecture.reference"


def _contracts_without_contract(project: Path) -> str:
    _replace(
        project / ".ai-python/policy.toml",
        'graph = "flat"',
        'graph = "contracts"',
    )
    (project / ".ai-python/config/importlinter.ini").write_text(
        "[importlinter]\nroot_package = example\n", encoding="utf-8"
    )
    return "contract mode requires at least one contract"


def _custom_docstrings_without_categories(project: Path) -> str:
    _replace(
        project / ".ai-python/policy.toml",
        'scope = "public"',
        'scope = "custom"',
    )
    return "categories must not be empty"


def _empty_test_categories(project: Path) -> str:
    _replace(
        project / ".ai-python/policy.toml",
        'categories = ["unit", "regression"]',
        "categories = []",
    )
    return "categories must not be empty"


def _bad_review_threshold(project: Path) -> str:
    _replace(project / ".ai-python/policy.toml", "function_lines = 60", "function_lines = 0")
    return "positive integer"


def _unsupported_profile(project: Path) -> str:
    _replace(
        project / ".ai-python/policy.toml",
        'profiles = ["library"]',
        'profiles = ["library", "quantum"]',
    )
    return "unsupported profiles"


def _bad_quality(project: Path) -> str:
    _replace(project / ".ai-python/policy.toml", 'quality = "standard"', 'quality = "maximum"')
    return "quality must be"


def _incompatible_schema(project: Path) -> str:
    _replace(project / ".ai-python/policy.toml", "schema = 1", "schema = 2")
    return "schema must be 1"


def _missing_answers_file(project: Path) -> str:
    (project / ".copier-answers.ai-python-kit.yml").unlink()
    return "lineage file"


def _expired_exception(project: Path) -> str:
    with (project / ".ai-python/policy.toml").open("a", encoding="utf-8") as handle:
        handle.write(
            """
[[exceptions]]
id = "old"
rule = "ruff.C901"
target = "src/example/core.py:greet"
reason = "Old baseline."
owner = "team"
approved_by = "maintainer"
approved_on = "2025-01-01"
expires_on = "2025-12-31"
approval_ref = "https://example.invalid/1"
"""
        )
    return "expired on"


MUTATIONS: list[tuple[Callable[[Path], str], str]] = [
    (_remove_agents, "missing AGENTS"),
    (_remove_agents_command, "missing command"),
    (_remove_native_config, "missing native config"),
    (_duplicate_root_ruff, "duplicate root config"),
    (_duplicate_tool_mypy, "duplicate pyproject config"),
    (_flat_with_two_children, "flat contract"),
    (_empty_profiles, "empty profiles"),
    (_unknown_key, "unknown key"),
    (_bad_source_path, "unsafe path"),
    (_bad_package, "bad package"),
    (_missing_architecture_reference, "missing reference"),
    (_contracts_without_contract, "contracts"),
    (_custom_docstrings_without_categories, "docstring categories"),
    (_empty_test_categories, "test categories"),
    (_bad_review_threshold, "review threshold"),
    (_unsupported_profile, "unsupported profile"),
    (_bad_quality, "bad quality"),
    (_incompatible_schema, "schema"),
    (_missing_answers_file, "answers"),
    (_expired_exception, "exception expiry"),
]


def test_rendered_default_policy_is_valid(render: Callable[..., Path]) -> None:
    project = render()
    result = _validate(project)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(("mutation", "label"), MUTATIONS, ids=[label for _, label in MUTATIONS])
def test_policy_mutations_fail_with_actionable_diagnostics(
    render: Callable[..., Path], mutation: Callable[[Path], str], label: str
) -> None:
    project = render()
    expected = mutation(project)
    result = _validate(project)
    assert result.returncode == 1, f"{label} unexpectedly passed: {result.stdout}"
    assert expected in result.stderr, f"{label}: expected '{expected}' in:\n{result.stderr}"
