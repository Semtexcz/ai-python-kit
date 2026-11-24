"""Copier rendering, profile composition, and seed behavior."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.support import KIT_ROOT, copier_copy, run


def _policy(project: Path) -> str:
    return (project / ".ai-python/policy.toml").read_text(encoding="utf-8")


def _copy_failure(destination: Path, **answers: object) -> object:
    command: list[str] = [sys.executable, "-m", "copier", "copy", "--defaults"]
    for key, value in answers.items():
        command.extend(["-d", f"{key}={value}"])
    command.extend([str(KIT_ROOT), str(destination)])
    return run(command, cwd=destination.parent)


def test_default_render_has_expected_ownership_and_seed(render) -> None:
    project = render()
    expected = {
        "AGENTS.md",
        "README.md",
        "pyproject.toml",
        ".python-version",
        ".copier-answers.ai-python-kit.yml",
        ".ai-python/policy.toml",
        ".ai-python/kit/justfile",
        ".ai-python/kit/adapter/ai_python_policy.py",
        ".ai-python/kit/references/evidence.md",
        ".ai-python/kit/skills/python-implement/SKILL.md",
        "src/example/__init__.py",
        "src/example/core.py",
        "tests/test_greeting.py",
        "docs/architecture.md",
    }
    for relative in expected:
        assert (project / relative).exists(), relative
    assert not (project / "src/example/cli.py").exists()
    assert 'profiles = ["library"]' in _policy(project)
    assert 'style = "modular"' in _policy(project)
    assert 'graph = "flat"' in _policy(project)
    assert 'format = "google"' in _policy(project)
    answers = (project / ".copier-answers.ai-python-kit.yml").read_text(encoding="utf-8")
    assert "_src_path:" in answers
    assert "profiles:" not in answers
    assert "architecture_resolved:" not in answers
    assert "just --justfile .ai-python/kit/justfile" in (project / "AGENTS.md").read_text(
        encoding="utf-8"
    )


def test_library_cli_scientific_composes_expected_seed(render) -> None:
    project = render(
        profile_cli="true",
        profile_scientific="true",
        display_name="Science CLI",
        distribution_name="science-cli",
        package="science_cli",
    )
    policy = _policy(project)
    assert 'profiles = ["library", "cli", "scientific"]' in policy
    assert 'format = "numpy"' in policy
    assert 'graph = "contracts"' in policy
    assert 'style = "modular"' in policy
    assert (project / "src/science_cli/cli.py").exists()
    assert (project / "tests/test_cli.py").exists()
    pyproject = (project / "pyproject.toml").read_text(encoding="utf-8")
    assert '"science-cli" = "science_cli.cli:main"' in pyproject
    guidance = (project / "docs/engineering-guidance.md").read_text(encoding="utf-8")
    assert "Scientific computing" in guidance
    assert "Command line" in guidance


def test_explicit_docstring_format_overrides_profile_recommendation(render) -> None:
    project = render(
        profile_scientific="true",
        docstring_format="sphinx",
        display_name="Explicit Docs",
        distribution_name="explicit-docs",
        package="explicit_docs",
    )
    assert 'format = "sphinx"' in _policy(project)


def test_backend_desktop_auto_is_unresolved_and_explicit_style_wins(render) -> None:
    unresolved = render(
        profile_backend="true",
        profile_desktop="true",
        display_name="Conflict",
        distribution_name="conflict",
        package="conflict",
    )
    assert 'style = "conflict"' in _policy(unresolved)
    result = run(
        [sys.executable, ".ai-python/kit/adapter/ai_python_policy.py", "validate"],
        cwd=unresolved,
    )
    assert result.returncode == 1
    assert "architecture" in result.stderr

    resolved = copier_copy(
        unresolved.parent / "resolved",
        profile_backend="true",
        profile_desktop="true",
        architecture_style="layered",
        display_name="Conflict",
        distribution_name="conflict",
        package="conflict",
    )
    assert 'style = "layered"' in _policy(resolved)
    result = run(
        [sys.executable, ".ai-python/kit/adapter/ai_python_policy.py", "validate"],
        cwd=resolved,
    )
    assert result.returncode == 0, result.stderr


def test_strict_preset_seeds_native_strictness_and_coverage(render) -> None:
    project = render(
        quality="strict",
        display_name="Strict",
        distribution_name="strict",
        package="strict",
    )
    policy = _policy(project)
    assert 'quality = "strict"' in policy
    assert 'scope = "all"' in policy
    assert 'public_detail = "detailed"' in policy
    assert 'private_detail = "standard"' in policy
    mypy = (project / ".ai-python/config/mypy.ini").read_text(encoding="utf-8")
    assert "strict = True" in mypy
    assert "disallow_any_explicit = True" in mypy
    coverage = (project / ".ai-python/config/coverage.ini").read_text(encoding="utf-8")
    assert "branch = True" in coverage
    assert "fail_under = 90" in coverage
    ruff = (project / ".ai-python/config/ruff.toml").read_text(encoding="utf-8")
    assert "max-complexity = 10" in ruff
    assert "max-args = 5" in ruff


def test_minimal_preset_seeds_line_coverage_and_summary_docs(render) -> None:
    project = render(
        quality="minimal",
        display_name="Minimal",
        distribution_name="minimal",
        package="minimal",
    )
    policy = _policy(project)
    assert 'public_detail = "summary"' in policy
    coverage = (project / ".ai-python/config/coverage.ini").read_text(encoding="utf-8")
    assert "branch = False" in coverage
    assert "fail_under = 60" in coverage
    ruff = (project / ".ai-python/config/ruff.toml").read_text(encoding="utf-8")
    assert '"D417"' in ruff
    assert "max-complexity = 15" in ruff


def test_hexagonal_seed_has_contracts_and_adapters(render) -> None:
    project = render(
        architecture_style="hexagonal",
        profile_cli="true",
        display_name="Hex",
        distribution_name="hex",
        package="hexpkg",
    )
    assert 'style = "hexagonal"' in _policy(project)
    assert (project / "src/hexpkg/domain/greeting.py").exists()
    assert (project / "src/hexpkg/ports/greeting.py").exists()
    assert (project / "src/hexpkg/adapters/console.py").exists()
    assert (project / "src/hexpkg/composition.py").exists()
    assert (project / "src/hexpkg/cli.py").exists()
    contracts = (project / ".ai-python/config/importlinter.ini").read_text(encoding="utf-8")
    assert "domain-independence" in contracts
    assert "ports-independence" in contracts


def test_adopt_mode_renders_overlay_and_proposals_only(render) -> None:
    project = render(
        creation_mode="adopt",
        display_name="Legacy",
        distribution_name="legacy",
        package="legacy",
    )
    assert (project / ".ai-python/kit/justfile").exists()
    assert (project / ".ai-python/kit/bootstrap/adopt/AGENTS-snippet.md").exists()
    assert (project / ".ai-python/policy.toml").exists()
    assert (project / ".copier-answers.ai-python-kit.yml").exists()
    for relative in (
        "src",
        "tests",
        "docs",
        "README.md",
        "AGENTS.md",
        "justfile",
        "pyproject.toml",
    ):
        assert not (project / relative).exists(), relative


def test_empty_profile_selection_renders_but_fails_validation(render) -> None:
    project = render(
        profile_library="false",
        display_name="No Profile",
        distribution_name="no-profile",
        package="no_profile",
    )
    assert "profiles = []" in _policy(project)
    result = run(
        [sys.executable, ".ai-python/kit/adapter/ai_python_policy.py", "validate"],
        cwd=project,
    )
    assert result.returncode == 1
    assert "profiles must not be empty" in result.stderr


@pytest.mark.parametrize(
    ("answers", "message"),
    [
        ({"display_name": ""}, "display_name must not be blank"),
        ({"package": "Bad-Package"}, "package must be a lowercase dotted"),
        ({"distribution_name": "bad name"}, "distribution_name must use"),
        ({"source_dir": "/tmp/src"}, "source_dir must be a non-empty"),
        ({"tests_dir": "../tests"}, "tests_dir must be a non-empty"),
        ({"quality": "maximum"}, "Invalid choice"),
    ],
)
def test_invalid_answers_fail_before_promotion(
    tmp_path: Path, answers: dict[str, str], message: str
) -> None:
    result = _copy_failure(tmp_path / "invalid", **answers)
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert message in combined
