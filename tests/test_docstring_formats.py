"""Real pydoclint behavior for each supported structured docstring format."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.support import assert_stage, copier_copy, run, tool_env

pytestmark = pytest.mark.e2e

FORMATS = {
    "google": ("    name: Display name to greet.", "    nombre: Display name to greet."),
    "numpy": ("name : str", "nombre : str"),
    "sphinx": (":param name: Display name to greet.", ":param nombre: Display name to greet."),
}


def _project(tmp_path: Path, docstring_format: str) -> Path:
    project = copier_copy(
        tmp_path / docstring_format,
        quality="minimal",
        docstring_format=docstring_format,
        display_name=f"Docs {docstring_format}",
        distribution_name=f"docs-{docstring_format}",
        package=f"docs_{docstring_format}",
    )
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


@pytest.mark.parametrize("docstring_format", sorted(FORMATS))
def test_wrong_argument_name_fails_structured_docstring_check(
    tmp_path: Path, docstring_format: str
) -> None:
    project = _project(tmp_path, docstring_format)
    old, new = FORMATS[docstring_format]
    core = project / f"src/docs_{docstring_format}/core.py"
    text = core.read_text(encoding="utf-8")
    assert old in text
    core.write_text(text.replace(old, new, 1), encoding="utf-8")
    result = _check(project)
    assert result.returncode != 0
    assert_stage(result, "docs", "FAIL")
    assert "DOC" in result.stdout + result.stderr


def test_pep257_reports_the_structured_check_as_skipped(tmp_path: Path) -> None:
    project = _project(tmp_path, "pep257")
    result = _check(project)
    assert result.returncode == 0, result.stdout + result.stderr
    assert any(line.startswith("SKIP docs.pydoclint") for line in result.stdout.splitlines())
