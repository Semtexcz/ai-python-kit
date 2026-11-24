"""Native plugin availability is a required verification prerequisite."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import run, tool_env

pytestmark = pytest.mark.e2e


def test_flake8_requires_the_pydoclint_plugin(tmp_path: Path) -> None:
    venv = tmp_path / "venv"
    created = run(["uv", "venv", "--python", "3.12", str(venv)], cwd=tmp_path, env=tool_env())
    assert created.returncode == 0, created.stdout + created.stderr
    installed = run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(venv / "bin/python"),
            "flake8==7.5.0",
        ],
        cwd=tmp_path,
        env=tool_env(),
    )
    assert installed.returncode == 0, installed.stdout + installed.stderr
    module = tmp_path / "module.py"
    module.write_text('"""Module."""\n', encoding="utf-8")
    result = run(
        [
            venv / "bin/flake8",
            "--require-plugins",
            "pydoclint",
            "--select",
            "DOC001",
            str(module),
        ],
        cwd=tmp_path,
        env=tool_env(),
    )
    assert result.returncode != 0
    assert "pydoclint" in (result.stdout + result.stderr)
