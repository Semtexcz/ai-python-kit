"""Built distributions run without development or kit dependencies."""

from __future__ import annotations

import glob
import sys
from pathlib import Path

import pytest

from tests.support import copier_copy, run, tool_env

pytestmark = pytest.mark.e2e


def _build_and_install(project: Path, venv: Path) -> None:
    build = run(["uv", "build", "--wheel", "--out-dir", "dist"], cwd=project, env=tool_env())
    assert build.returncode == 0, build.stdout + build.stderr
    created = run(["uv", "venv", "--python", "3.12", str(venv)], cwd=project, env=tool_env())
    assert created.returncode == 0, created.stdout + created.stderr
    wheels = glob.glob(str(project / "dist" / "*.whl"))
    assert len(wheels) == 1
    install = run(
        ["uv", "pip", "install", "--python", str(venv / "bin/python"), "--no-deps", wheels[0]],
        cwd=project,
        env=tool_env(),
    )
    assert install.returncode == 0, install.stdout + install.stderr


def test_library_builds_and_imports_without_kit_dependencies(tmp_path: Path) -> None:
    project = copier_copy(tmp_path / "library")
    lock = run(["uv", "lock"], cwd=project, env=tool_env())
    assert lock.returncode == 0, lock.stdout + lock.stderr
    venv = tmp_path / "venv"
    _build_and_install(project, venv)
    result = run(
        [venv / "bin/python", "-c", "import example; print(example.greet('Ada'))"],
        cwd=tmp_path,
        env=tool_env(),
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Hello, Ada!"


def test_cli_starter_runs_and_reports_invalid_input(tmp_path: Path) -> None:
    if sys.platform != "linux":
        pytest.skip("Reference acceptance matrix is Linux")
    project = copier_copy(
        tmp_path / "cli",
        profile_cli="true",
        display_name="CLI Packaging",
        distribution_name="cli-packaging",
        package="cli_packaging",
    )
    lock = run(["uv", "lock"], cwd=project, env=tool_env())
    assert lock.returncode == 0, lock.stdout + lock.stderr
    venv = tmp_path / "venv"
    _build_and_install(project, venv)
    command = venv / "bin/cli-packaging"
    valid = run([command, "World"], cwd=tmp_path, env=tool_env())
    assert valid.returncode == 0, valid.stdout + valid.stderr
    assert valid.stdout.strip() == "Hello, World!"
    invalid = run([command, ""], cwd=tmp_path, env=tool_env())
    assert invalid.returncode == 2
    assert "name must not be blank" in invalid.stderr
