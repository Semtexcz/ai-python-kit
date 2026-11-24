"""Tagged Copier update, conflict, and rollback behavior."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from tests.support import KIT_ROOT, run


def _git(cwd: Path, *arguments: str) -> None:
    result = run(["git", *arguments], cwd=cwd)
    assert result.returncode == 0, result.stdout + result.stderr


def _init_repo(path: Path) -> None:
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "test@example.invalid")
    _git(path, "config", "user.name", "Test")
    _git(path, "add", "-A")
    _git(path, "commit", "-qm", "checkpoint")


def _tag(path: Path, tag: str) -> None:
    _git(path, "add", "-A")
    staged = run(["git", "diff", "--cached", "--quiet"], cwd=path)
    if staged.returncode != 0:
        _git(path, "commit", "-qm", tag)
    _git(path, "tag", tag)


def _kit_source(tmp_path: Path) -> Path:
    source = tmp_path / "kit-source"
    source.mkdir()
    shutil.copy2(KIT_ROOT / "copier.yml", source / "copier.yml")
    shutil.copy2(KIT_ROOT / "_docstrings.jinja", source / "_docstrings.jinja")
    shutil.copytree(KIT_ROOT / "template", source / "template")
    _init_repo(source)
    _tag(source, "v0.1.0")
    return source


def _render(source: Path, destination: Path) -> None:
    result = run(
        [
            sys.executable,
            "-m",
            "copier",
            "copy",
            "--defaults",
            "--vcs-ref",
            "v0.1.0",
            str(source),
            str(destination),
        ],
        cwd=destination.parent,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    _init_repo(destination)


def _update(destination: Path, tag: str) -> object:
    return run(
        [
            sys.executable,
            "-m",
            "copier",
            "update",
            "--answers-file",
            ".copier-answers.ai-python-kit.yml",
            "--vcs-ref",
            tag,
            "--conflict",
            "rej",
            "--skip-answered",
        ],
        cwd=destination,
    )


def test_tagged_update_preserves_project_owned_files(tmp_path: Path) -> None:
    source = _kit_source(tmp_path)
    project = tmp_path / "project"
    _render(source, project)
    original = {
        relative: (project / relative).read_bytes()
        for relative in (
            "src/example/core.py",
            "tests/test_greeting.py",
            "AGENTS.md",
        )
    }
    managed = project / ".ai-python/kit/references/evidence.md"
    before = managed.read_text(encoding="utf-8")

    with (source / "template/.ai-python/kit/references/evidence.md").open(
        "a", encoding="utf-8"
    ) as handle:
        handle.write("\nTagged update marker.\n")
    _tag(source, "v0.2.0")

    result = _update(project, "v0.2.0")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Tagged update marker." in managed.read_text(encoding="utf-8")
    assert before != managed.read_text(encoding="utf-8")
    for relative, content in original.items():
        assert (project / relative).read_bytes() == content, relative
    answers = (project / ".copier-answers.ai-python-kit.yml").read_text(encoding="utf-8")
    assert "v0.2.0" in answers


def test_update_conflict_is_visible_and_rollback_restores_checkpoint(
    tmp_path: Path,
) -> None:
    source = _kit_source(tmp_path)
    project = tmp_path / "project"
    _render(source, project)
    managed = project / ".ai-python/kit/references/evidence.md"
    with managed.open("a", encoding="utf-8") as handle:
        handle.write("\nLocal project customization.\n")
    _git(project, "add", "-A")
    _git(project, "commit", "-qm", "local customization")

    with (source / "template/.ai-python/kit/references/evidence.md").open(
        "a", encoding="utf-8"
    ) as handle:
        handle.write("\nConflicting template change.\n")
    _tag(source, "v0.2.0")

    result = _update(project, "v0.2.0")
    assert result.returncode == 0, result.stdout + result.stderr
    reject = Path(str(managed) + ".rej")
    assert reject.is_file()
    combined = managed.read_text(encoding="utf-8") + reject.read_text(encoding="utf-8")
    assert "Local project customization." in combined
    assert "Conflicting template change." in combined

    _git(project, "checkout", "--", ".")
    reject.unlink()
    assert "Local project customization." in managed.read_text(encoding="utf-8")
    assert "Conflicting template change." not in managed.read_text(encoding="utf-8")
    answers = (project / ".copier-answers.ai-python-kit.yml").read_text(encoding="utf-8")
    assert "v0.2.0" not in answers


def test_incompatible_policy_schema_fails_before_acceptance(tmp_path: Path) -> None:
    source = _kit_source(tmp_path)
    project = tmp_path / "project"
    _render(source, project)
    policy = project / ".ai-python/policy.toml"
    policy.write_text(
        policy.read_text(encoding="utf-8").replace("schema = 1", "schema = 2"),
        encoding="utf-8",
    )
    result = run(
        [sys.executable, ".ai-python/kit/adapter/ai_python_policy.py", "validate"],
        cwd=project,
    )
    assert result.returncode == 1
    assert "schema must be 1" in result.stderr
