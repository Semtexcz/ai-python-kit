"""Upstream skill inventory and file hash checks."""

from __future__ import annotations

import hashlib
import tomllib

from tests.support import KIT_ROOT

KIT = KIT_ROOT / "template/.ai-python/kit"
INVENTORY = KIT / "upstream-skills.toml"
SKILLS = KIT / "skills"
REQUIRED_FIELDS = {
    "name",
    "repository",
    "path",
    "commit",
    "upstream_version",
    "license",
    "notice",
    "license_file",
    "distribution",
    "profiles",
    "purpose",
    "incompatibilities",
    "changes",
    "files",
}


def _inventory() -> list[dict[str, object]]:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    assert data["schema"] == 1
    skills = data["skills"]
    assert isinstance(skills, list)
    return skills


def test_inventory_has_required_entries_and_fields() -> None:
    entries = _inventory()
    names = {entry["name"] for entry in entries}
    assert names == {
        "modern-python",
        "python-pytest",
        "python-best-practices",
        "python-async-best-practices",
    }
    for entry in entries:
        assert set(entry) >= REQUIRED_FIELDS, entry.get("name")
        assert len(str(entry["commit"])) == 40
        assert str(entry["repository"]).startswith("https://github.com/")
        assert isinstance(entry["profiles"], list) and entry["profiles"]
        assert isinstance(entry["incompatibilities"], list) and entry["incompatibilities"]
        assert entry["changes"] == "none"


def test_vendored_files_match_recorded_hashes() -> None:
    entry = next(item for item in _inventory() if item["name"] == "modern-python")
    assert entry["distribution"] == "vendored"
    files = entry["files"]
    assert isinstance(files, dict)
    directory = SKILLS / "modern-python"
    for relative, digest in files.items():
        path = directory / str(relative)
        assert path.is_file(), relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == digest, relative
    included = {
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file() and path.name != "NOTICE.md"
    }
    assert included == set(files)
    assert (KIT / str(entry["license_file"])).is_file()
    assert (KIT / str(entry["notice"])).is_file()


def test_reference_entries_ship_no_files() -> None:
    references = [item for item in _inventory() if item["distribution"] == "reference"]
    assert {item["name"] for item in references} == {
        "python-pytest",
        "python-best-practices",
        "python-async-best-practices",
    }
    for entry in references:
        assert entry["files"] == {}
        assert str(entry["notice"]).endswith("#license")
        assert entry["license"] == "MIT"


def test_upstream_policy_records_precedence_and_fallback() -> None:
    text = (KIT / "references/upstream-policy.md").read_text(encoding="utf-8")
    assert "project policy wins" in text.lower()
    assert "does not provide a copyright and permission notice" in text
    assert "CC BY-SA 4.0" in text
