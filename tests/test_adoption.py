"""Safe adoption preflight and preservation of existing project content."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

from tests.support import ADAPTER_PATH, assert_stage, copier_copy, run, tool_env


def _git(cwd: Path, *arguments: str) -> None:
    result = run(["git", *arguments], cwd=cwd)
    assert result.returncode == 0, result.stdout + result.stderr


def _init_repo(path: Path) -> None:
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "test@example.invalid")
    _git(path, "config", "user.name", "Test")
    _git(path, "add", "-A")
    _git(path, "commit", "-qm", "existing project")


def _preflight(project: Path) -> object:
    return run(
        [sys.executable, ADAPTER_PATH, "adoption-preflight", "."],
        cwd=project,
    )


def _existing_project(tmp_path: Path) -> Path:
    project = copier_copy(
        tmp_path / "existing",
        display_name="Legacy App",
        distribution_name="legacy-app",
        package="legacy_app",
    )
    shutil.rmtree(project / ".ai-python")
    for relative in (
        ".copier-answers.ai-python-kit.yml",
        "AGENTS.md",
        "justfile",
        ".github",
        "docs/engineering-guidance.md",
    ):
        path = project / relative
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    (project / "AGENTS.md").write_text(
        "# Existing instructions\n\nKeep this project-specific text.\n",
        encoding="utf-8",
    )
    (project / "README.md").write_text("# Legacy App\n\nExisting README.\n", encoding="utf-8")
    (project / ".ai-docs").mkdir()
    (project / ".ai-docs/notes.md").write_text("Other kit namespace.\n", encoding="utf-8")
    (project / ".github").mkdir()
    (project / ".github/workflows").mkdir()
    (project / ".github/workflows/custom.yml").write_text("name: Custom\n", encoding="utf-8")
    lock = run(["uv", "lock"], cwd=project, env=tool_env())
    assert lock.returncode == 0, lock.stdout + lock.stderr
    _init_repo(project)
    return project


def test_preflight_refuses_dirty_colliding_and_symlink_targets(tmp_path: Path) -> None:
    project = _existing_project(tmp_path)
    assert _preflight(project).returncode == 0

    (project / "README.md").write_text("# Dirty\n", encoding="utf-8")
    result = _preflight(project)
    assert result.returncode == 1
    assert "not clean" in result.stderr
    _git(project, "checkout", "--", ".")

    (project / ".ai-python").mkdir()
    result = _preflight(project)
    assert result.returncode == 1
    assert "already exists" in result.stderr
    (project / ".ai-python").rmdir()

    outside = tmp_path / "outside"
    outside.mkdir()
    (project / ".ai-python").symlink_to(outside)
    result = _preflight(project)
    assert result.returncode == 1
    assert "symlink" in result.stderr
    (project / ".ai-python").unlink()


@pytest.mark.e2e
def test_adoption_preserves_source_tests_instructions_and_gate(tmp_path: Path) -> None:
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is required for the adoption verification test")
    project = _existing_project(tmp_path)
    source_before = {
        path.relative_to(project): path.read_bytes() for path in (project / "src").rglob("*.py")
    }
    tests_before = {
        path.relative_to(project): path.read_bytes() for path in (project / "tests").rglob("*.py")
    }
    agents_before = (project / "AGENTS.md").read_text(encoding="utf-8")

    proposal = copier_copy(
        tmp_path / "proposal",
        creation_mode="adopt",
        display_name="Legacy App",
        distribution_name="legacy-app",
        package="legacy_app",
    )
    assert _preflight(project).returncode == 0
    shutil.copytree(proposal / ".ai-python", project / ".ai-python")
    shutil.copy2(
        proposal / ".copier-answers.ai-python-kit.yml",
        project / ".copier-answers.ai-python-kit.yml",
    )
    with (project / "AGENTS.md").open("a", encoding="utf-8") as handle:
        handle.write(
            "\n## AI Python Kit routing\n\n"
            "just --justfile .ai-python/kit/justfile --working-directory . check\n"
        )
    shutil.copy2(
        project / ".ai-python/kit/bootstrap/adopt/justfile",
        project / "justfile",
    )

    assert {
        path.relative_to(project): path.read_bytes() for path in (project / "src").rglob("*.py")
    } == source_before
    assert {
        path.relative_to(project): path.read_bytes() for path in (project / "tests").rglob("*.py")
    } == tests_before
    agents_after = (project / "AGENTS.md").read_text(encoding="utf-8")
    assert agents_before in agents_after
    assert (project / ".ai-docs/notes.md").read_text(encoding="utf-8") == ("Other kit namespace.\n")
    assert (project / ".github/workflows/custom.yml").is_file()

    just = Path(sys.executable).parent / "just"
    result = run(
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
    assert result.returncode == 0, result.stdout + result.stderr
    assert_stage(result, "config", "PASS")
    assert_stage(result, "tests", "PASS")

    (project / "ruff.toml").write_text("line-length = 90\n", encoding="utf-8")
    conflict = run(
        [sys.executable, ".ai-python/kit/adapter/ai_python_policy.py", "validate"],
        cwd=project,
    )
    assert conflict.returncode == 1
    assert "duplicate native configuration 'ruff.toml'" in conflict.stderr
    (project / "ruff.toml").unlink()
    assert (
        run(
            [sys.executable, ".ai-python/kit/adapter/ai_python_policy.py", "validate"],
            cwd=project,
        ).returncode
        == 0
    )
