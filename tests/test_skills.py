"""Agent Skills structure, routing, and link checks."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest
import yaml

from tests.support import KIT_ROOT, run

SKILLS = KIT_ROOT / "template/.ai-python/kit/skills"
REQUIRED = {
    "python-implement",
    "python-review",
    "python-audit",
    "python-verify",
    "python-architecture",
    "python-dependencies",
}
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), path
    _, raw, _ = text.split("---", 2)
    data = yaml.safe_load(raw)
    assert isinstance(data, dict)
    return data


def test_required_skills_exist_and_metadata_matches_directory() -> None:
    found = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
    assert found >= REQUIRED
    for name in found:
        data = _frontmatter(SKILLS / name / "SKILL.md")
        assert data.get("name") == name
        description = data.get("description")
        assert isinstance(description, str) and len(description.strip()) > 20
        assert len(str(description)) <= 1024


def test_skills_validate_with_pinned_upstream_reference() -> None:
    validator = shutil.which("skills-ref")
    if validator is None:
        pytest.skip("skills-ref is not installed; run the maintainer validation command")
    for skill in sorted(SKILLS.glob("*/SKILL.md")):
        result = run([validator, "validate", skill.parent], cwd=KIT_ROOT)
        assert result.returncode == 0, result.stdout + result.stderr


def test_relative_skill_links_resolve() -> None:
    markdown = list(SKILLS.rglob("*.md"))
    assert markdown
    for path in markdown:
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = target.split("#", 1)[0]
            if not relative:
                continue
            resolved = (path.parent / relative).resolve()
            assert resolved.exists(), f"{path}: broken link {target}"


def test_root_routing_block_names_every_workflow_skill() -> None:
    agents = (KIT_ROOT / "template/AGENTS.md.jinja").read_text(encoding="utf-8")
    for name in REQUIRED:
        assert f".ai-python/kit/skills/{name}/SKILL.md" in agents


def test_no_duplicate_agent_specific_skill_directories() -> None:
    for relative in (".agents/skills", "template/.agents/skills", ".claude/skills"):
        assert not (KIT_ROOT / relative).exists(), relative


def test_reference_validator_rejects_invalid_metadata(tmp_path: Path) -> None:
    validator = shutil.which("skills-ref")
    if validator is None:
        pytest.skip("skills-ref is not installed")
    source = SKILLS / "python-verify"
    cases = {
        "missing-description": (
            "---\nname: python-verify\n---\n\n# Missing description\n",
            "description",
        ),
        "name-mismatch": (
            "---\nname: other-name\ndescription: " + "x" * 40 + "\n---\n",
            "name",
        ),
        "invalid-yaml": ("---\nname: [unclosed\n---\n", "yaml"),
    }
    for label, (content, expected) in cases.items():
        directory = tmp_path / label / source.name
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text(content, encoding="utf-8")
        if label == "name-mismatch":
            target = directory.parent / "directory-mismatch"
            directory.rename(target)
            directory = target
        result = run([validator, "validate", directory], cwd=tmp_path)
        assert result.returncode != 0, label
        assert expected.lower() in (result.stdout + result.stderr).lower(), label


def test_vendored_skill_keeps_notice_and_license() -> None:
    directory = SKILLS / "modern-python"
    assert (directory / "NOTICE.md").is_file()
    assert (directory / "LICENSE").is_file()
    license_text = (directory / "LICENSE").read_text(encoding="utf-8")
    assert "Attribution-ShareAlike 4.0" in license_text
    notice = (directory / "NOTICE.md").read_text(encoding="utf-8")
    assert "149d7b21f4067765b82e67029730b42d228ef4b4" in notice


def test_reference_only_skills_are_not_redistributed() -> None:
    assert not (SKILLS / "python-pytest").exists()
    assert not (SKILLS / "python-best-practices").exists()
    assert not (SKILLS / "python-async-best-practices").exists()
