"""Real Import Linter contracts for layered, hexagonal, and cycle cases."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.support import assert_stage, copier_copy, run, tool_env

pytestmark = pytest.mark.e2e


def _render(tmp_path: Path, **answers: object) -> Path:
    project = copier_copy(tmp_path / "project", **answers)
    lock = run(["uv", "lock"], cwd=project, env=tool_env())
    assert lock.returncode == 0, lock.stdout + lock.stderr
    return project


def _check(project: Path) -> object:
    just = Path(sys.executable).parent / "just"
    return run(
        [
            just,
            "--justfile",
            ".ai-python/kit/justfile",
            "--working-directory",
            ".",
            "check",
        ],
        cwd=project,
        env=tool_env(),
    )


def test_layered_contract_rejects_transitive_upward_import(tmp_path: Path) -> None:
    project = _render(
        tmp_path,
        architecture_style="layered",
        profile_cli="true",
        display_name="Layered",
        distribution_name="layered",
        package="layered_app",
    )
    (project / "src/layered_app/domain/helper.py").write_text(
        '"""Helper."""\n\nfrom layered_app.presentation.cli import main\n\nVALUE = main\n',
        encoding="utf-8",
    )
    (project / "src/layered_app/domain/greeting.py").write_text(
        '"""Domain."""\n\nfrom layered_app.domain.helper import VALUE\n\n\n'
        'def greet(name: str) -> str:\n    """Greet."""\n    _ = VALUE\n    return name\n',
        encoding="utf-8",
    )
    result = _check(project)
    assert result.returncode != 0
    assert_stage(result, "architecture", "FAIL")
    assert "BROKEN" in result.stdout


def test_hexagonal_contract_rejects_domain_adapter_import(tmp_path: Path) -> None:
    project = _render(
        tmp_path,
        architecture_style="hexagonal",
        display_name="Hex",
        distribution_name="hex",
        package="hex_app",
    )
    (project / "src/hex_app/domain/greeting.py").write_text(
        '"""Domain."""\n\nfrom hex_app.adapters.console import ConsolePresenter\n\n\n'
        'def greet(name: str) -> str:\n    """Greet."""\n'
        "    _ = ConsolePresenter\n    return name\n",
        encoding="utf-8",
    )
    result = _check(project)
    assert result.returncode != 0
    assert_stage(result, "architecture", "FAIL")
    assert "BROKEN" in result.stdout


def test_modular_acyclic_contract_rejects_sibling_cycle(tmp_path: Path) -> None:
    project = _render(
        tmp_path,
        display_name="Cycle",
        distribution_name="cycle",
        package="cycle_app",
    )
    (project / "src/cycle_app/cli.py").write_text(
        '"""Command."""\n\nfrom cycle_app.core import greet\n\nVALUE = greet("x")\n',
        encoding="utf-8",
    )
    core = project / "src/cycle_app/core.py"
    core.write_text(
        '"""Core."""\n\nfrom __future__ import annotations\n\n'
        "from cycle_app.cli import VALUE\n\n\ndef greet(name: str) -> str:\n"
        '    """Greet."""\n    return f"{name}:{VALUE}"\n',
        encoding="utf-8",
    )
    text = (project / ".ai-python/policy.toml").read_text(encoding="utf-8")
    (project / ".ai-python/policy.toml").write_text(
        text.replace('graph = "flat"', 'graph = "contracts"'), encoding="utf-8"
    )
    result = _check(project)
    assert result.returncode != 0
    assert_stage(result, "architecture", "FAIL")
    assert "BROKEN" in result.stdout


def test_custom_contract_rejects_documented_boundary(tmp_path: Path) -> None:
    project = _render(
        tmp_path,
        architecture_style="custom",
        profile_cli="true",
        display_name="Custom CLI",
        distribution_name="custom-cli",
        package="custom_cli",
    )
    core = project / "src/custom_cli/core.py"
    text = core.read_text(encoding="utf-8")
    core.write_text(
        text.replace(
            "from __future__ import annotations\n",
            "from __future__ import annotations\n\nfrom custom_cli.cli import main\n",
        )
        + "\n\nCOMMAND = main\n",
        encoding="utf-8",
    )
    result = _check(project)
    assert result.returncode != 0
    assert_stage(result, "architecture", "FAIL")
    assert "BROKEN" in result.stdout


def test_custom_contract_mode_renders_a_runnable_seed(tmp_path: Path) -> None:
    project = _render(
        tmp_path,
        architecture_style="custom",
        display_name="Custom",
        distribution_name="custom",
        package="custom_app",
    )
    result = _check(project)
    assert result.returncode == 0, result.stdout + result.stderr
    assert_stage(result, "architecture", "PASS")
