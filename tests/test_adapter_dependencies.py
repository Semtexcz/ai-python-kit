"""Direct dependency policy behavior of the adapter."""

from __future__ import annotations

import tomllib
from datetime import date
from pathlib import Path
from typing import Any

from tests.support import DEFAULT_PYPROJECT, base_policy, write_full_project

TODAY = date(2026, 11, 24)


def _pyproject(
    *,
    dependencies: str = "[]",
    optional: str = "",
    dev: str = "[]",
    legacy: str = "",
    dynamic: str = "[]",
) -> str:
    text = DEFAULT_PYPROJECT.replace("dependencies = []", f"dependencies = {dependencies}")
    text = text.replace("dev = []", f"dev = {dev}")
    if dynamic != "[]":
        text = text.replace(
            'requires-python = ">=3.12"', f'requires-python = ">=3.12"\ndynamic = {dynamic}'
        )
    if optional:
        text += f"\n[project.optional-dependencies]\n{optional}\n"
    if legacy:
        text += f"\n[tool.uv]\ndev-dependencies = {legacy}\n"
    return text


def _exception(
    *,
    identifier: str = "dep-1",
    rule: str = "dependency.runtime",
    target: str = "requests",
    approval: str = "2026-11-20",
    expiry: str = "2027-11-20",
    extra: str = "",
) -> str:
    return f"""
[[exceptions]]
id = "{identifier}"
rule = "{rule}"
target = "{target}"
reason = "Approved for a bounded integration."
owner = "platform-team"
approved_by = "maintainer"
approved_on = "{approval}"
expires_on = "{expiry}"
approval_ref = "https://example.invalid/decisions/1"
{extra}"""


def _load(adapter: Any, root: Path, policy: str) -> Any:
    return adapter.Policy(root=root, data=tomllib.loads(policy), today=TODAY)


def test_stdlib_only_rejects_required_declaration(adapter: Any, tmp_path: Path) -> None:
    root = write_full_project(
        tmp_path,
        policy=base_policy(runtime="stdlib-only"),
        pyproject=_pyproject(dependencies='["requests"]'),
    )
    problems = adapter.check_dependencies(_load(adapter, root, base_policy(runtime="stdlib-only")))
    assert any("stdlib-only" in item and "requests" in item for item in problems)


def test_stdlib_only_rejects_marker_disabled_declaration(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy(runtime="stdlib-only")
    root = write_full_project(
        tmp_path,
        policy=policy,
        pyproject=_pyproject(dependencies="[\"requests; sys_platform == 'win32'\"]"),
    )
    problems = adapter.check_dependencies(_load(adapter, root, policy))
    assert any("requests" in item for item in problems)


def test_stdlib_only_rejects_optional_extra(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy(runtime="stdlib-only")
    root = write_full_project(
        tmp_path,
        policy=policy,
        pyproject=_pyproject(optional='remote = ["requests"]'),
    )
    problems = adapter.check_dependencies(_load(adapter, root, policy))
    assert any("runtime extra 'remote'" in item or "requests" in item for item in problems)


def test_exact_runtime_exception_permits_declaration(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy(runtime="stdlib-only", extra=_exception())
    root = write_full_project(
        tmp_path,
        policy=policy,
        pyproject=_pyproject(dependencies='["requests"]'),
    )
    problems = adapter.check_dependencies(_load(adapter, root, policy))
    assert not any("stdlib-only" in item for item in problems)


def test_expired_runtime_exception_does_not_permit(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy(
        runtime="stdlib-only",
        extra=_exception(expiry="2026-01-01"),
    )
    root = write_full_project(
        tmp_path,
        policy=policy,
        pyproject=_pyproject(dependencies='["requests"]'),
    )
    problems = adapter.check_dependencies(_load(adapter, root, policy))
    assert any("stdlib-only" in item for item in problems)


def test_development_stdlib_only_rejects_project_group(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy(development="stdlib-only")
    root = write_full_project(
        tmp_path,
        policy=policy,
        pyproject=_pyproject(dev='["hypothesis"]'),
    )
    problems = adapter.check_dependencies(_load(adapter, root, policy))
    assert any("development dependency 'hypothesis'" in item for item in problems)


def test_development_exception_permits_group_entry(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy(
        development="stdlib-only",
        extra=_exception(rule="dependency.development", target="hypothesis"),
    )
    root = write_full_project(
        tmp_path,
        policy=policy,
        pyproject=_pyproject(dev='["hypothesis"]'),
    )
    problems = adapter.check_dependencies(_load(adapter, root, policy))
    assert not any("stdlib-only" in item for item in problems)


def test_project_group_must_not_include_reserved_group(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy()
    root = write_full_project(
        tmp_path,
        policy=policy,
        pyproject=_pyproject(dev='[{include-group = "ai-python-kit"}]'),
    )
    problems = adapter.check_dependencies(_load(adapter, root, policy))
    assert any("must not include the reserved" in item for item in problems)


def test_unresolved_group_include_fails(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy()
    root = write_full_project(
        tmp_path,
        policy=policy,
        pyproject=_pyproject(dev='[{include-group = "missing"}]'),
    )
    problems = adapter.check_dependencies(_load(adapter, root, policy))
    assert any("unresolved group 'missing'" in item for item in problems)


def test_dynamic_dependency_metadata_fails(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy()
    root = write_full_project(
        tmp_path,
        policy=policy,
        pyproject=_pyproject(dynamic='["dependencies"]'),
    )
    problems = adapter.check_dependencies(_load(adapter, root, policy))
    assert any("dynamic dependency metadata" in item for item in problems)


def test_dependency_exception_target_must_be_normalized(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy(
        runtime="stdlib-only",
        extra=_exception(target="Requests"),
    )
    root = write_full_project(
        tmp_path,
        policy=policy,
        pyproject=_pyproject(dependencies='["Requests"]'),
    )
    problems = adapter.check_dependencies(_load(adapter, root, policy))
    assert any("must use the normalized package name" in item for item in problems)


def test_reserved_group_missing_tool_fails_validation(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy()
    pyproject = DEFAULT_PYPROJECT.replace('    "ruff==0.17.6",\n', "")
    root = write_full_project(tmp_path, policy=policy, pyproject=pyproject)
    problems = adapter.validate_policy(_load(adapter, root, policy))
    assert any("exact verification tool set" in item and "ruff" in item for item in problems)


def test_verify_groups_rejects_reserved_and_unknown(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy(verify_groups='["ai-python-kit", "missing"]')
    root = write_full_project(tmp_path, policy=policy, pyproject=DEFAULT_PYPROJECT)
    problems = adapter.validate_policy(_load(adapter, root, policy))
    assert any("must not list the reserved" in item for item in problems)
    assert any("unknown group 'missing'" in item for item in problems)


def test_invalid_exception_records_fail_validation(adapter: Any, tmp_path: Path) -> None:
    missing_fields = '\n[[exceptions]]\nid = "broken"\n'
    policy = base_policy(extra=missing_fields)
    root = write_full_project(tmp_path, policy=policy, pyproject=DEFAULT_PYPROJECT)
    problems = adapter.validate_policy(_load(adapter, root, policy))
    assert any("exception #1: missing" in item for item in problems)


def test_duplicate_and_expired_exceptions_fail_validation(adapter: Any, tmp_path: Path) -> None:
    records = _exception(identifier="same", expiry="2026-01-01") + _exception(
        identifier="same", target="other"
    )
    policy = base_policy(extra=records)
    root = write_full_project(tmp_path, policy=policy, pyproject=DEFAULT_PYPROJECT)
    problems = adapter.validate_policy(_load(adapter, root, policy))
    assert any("expired on" in item for item in problems)
    assert any("duplicate id 'same'" in item for item in problems)


def test_reversed_exception_dates_fail_validation(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy(extra=_exception(approval="2027-01-01", expiry="2026-01-01"))
    root = write_full_project(tmp_path, policy=policy, pyproject=DEFAULT_PYPROJECT)
    problems = adapter.validate_policy(_load(adapter, root, policy))
    assert any("approved_on is after expires_on" in item for item in problems)


def test_custom_architecture_requires_contracts(adapter: Any, tmp_path: Path) -> None:
    policy = base_policy(style="custom", graph="flat")
    root = write_full_project(tmp_path, policy=policy, pyproject=DEFAULT_PYPROJECT)
    problems = adapter.validate_policy(_load(adapter, root, policy))
    assert any("custom architecture requires graph" in item for item in problems)
