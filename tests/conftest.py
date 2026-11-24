"""Shared deterministic fixtures for the AI Python Kit tests."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path

import pytest

from tests.support import (
    ADAPTER_PATH,
    DEFAULT_PYPROJECT,
    TODAY,
    assert_stage,
    base_policy,
    copier_copy,
    run,
    tool_env,
    write_full_project,
)


@pytest.fixture(scope="session")
def adapter() -> object:
    """Load the shipped adapter as a module."""
    spec = importlib.util.spec_from_file_location("ai_python_policy", ADAPTER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def render(tmp_path: Path) -> Callable[..., Path]:
    """Render a project into a unique temporary directory."""

    def _render(**answers: object) -> Path:
        destination = tmp_path / "project"
        return copier_copy(destination, **answers)

    return _render


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """Create a minimal valid project for adapter unit tests."""
    return write_full_project(
        tmp_path / "project",
        policy=base_policy(),
        pyproject=DEFAULT_PYPROJECT,
    )


@pytest.fixture(scope="session")
def baseline(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Render and warm one default project for real-tool tests."""
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is required for end-to-end verification tests")
    just = Path(sys.executable).parent / "just"
    if not just.exists():
        pytest.skip("just is required for end-to-end verification tests")
    destination = tmp_path_factory.mktemp("baseline") / "project"
    copier_copy(destination)
    lock = run(["uv", "lock"], cwd=destination, env=tool_env())
    if lock.returncode != 0:
        raise AssertionError(f"uv lock failed:\n{lock.stdout}\n{lock.stderr}")
    sync = run(
        ["uv", "sync", "--group", "ai-python-kit"],
        cwd=destination,
        env=tool_env(),
    )
    if sync.returncode != 0:
        raise AssertionError(f"uv sync failed:\n{sync.stdout}\n{sync.stderr}")
    shutil.rmtree(destination / ".ai-python/.venv", ignore_errors=True)
    shutil.rmtree(destination / ".ai-python/cache", ignore_errors=True)
    return destination


def _ignore_generated(directory: str, names: list[str]) -> set[str]:
    ignored = {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}
    if Path(directory).name == ".ai-python":
        ignored.update({".venv", "cache", "evidence", ".coverage"})
    return ignored & set(names)


@pytest.fixture
def project_copy(tmp_path: Path, baseline: Path) -> Path:
    """Copy the warmed baseline project without environments or evidence."""
    destination = tmp_path / "project"
    shutil.copytree(baseline, destination, ignore=_ignore_generated)
    return destination


@pytest.fixture
def check(project_copy: Path) -> Callable[..., subprocess.CompletedProcess[str]]:
    """Run the real unified check on a copy of the baseline project."""
    just = Path(sys.executable).parent / "just"
    assert just.exists()

    def _check(
        *arguments: str,
        env: dict[str, str] | None = None,
        project: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        target = project or project_copy
        command = [
            just,
            "--justfile",
            ".ai-python/kit/justfile",
            "--working-directory",
            ".",
            "check",
            *arguments,
        ]
        result = run(command, cwd=target, env=tool_env(env))
        if project is None:
            shutil.rmtree(target / ".ai-python/.venv", ignore_errors=True)
            shutil.rmtree(target / ".ai-python/cache", ignore_errors=True)
        return result

    return _check


@pytest.fixture
def stage_assert() -> Callable[[subprocess.CompletedProcess[str], str, str], None]:
    """Expose the stage assertion helper as a fixture."""
    return assert_stage


@pytest.fixture
def fixed_today() -> date:
    """Return the frozen acceptance date used by adapter tests."""
    return TODAY
