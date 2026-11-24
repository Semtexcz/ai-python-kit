"""Real-tool verification of a rendered project and single-violation negatives."""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.support import assert_stage, run, stage_lines, tool_env

pytestmark = pytest.mark.e2e

CORE = "src/example/core.py"
TESTS = "tests/test_greeting.py"


def _append(project: Path, relative: str, text: str) -> None:
    path = project / relative
    current = path.read_text(encoding="utf-8").rstrip("\n")
    path.write_text(current + "\n\n\n" + text.lstrip("\n"), encoding="utf-8")


def _add_import(project: Path, relative: str, line: str) -> None:
    _replace(
        project,
        relative,
        "from __future__ import annotations\n",
        f"from __future__ import annotations\n\n{line}\n",
    )


def _replace(project: Path, relative: str, old: str, new: str) -> None:
    path = project / relative
    text = path.read_text(encoding="utf-8")
    assert old in text, f"missing fixture text in {relative}: {old}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _assert_failure(
    result: object,
    stage: str,
    diagnostic: str,
) -> None:
    assert result.returncode != 0, result.stdout + result.stderr
    assert_stage(result, stage, "FAIL")
    combined = result.stdout + result.stderr
    assert diagnostic in combined, combined[-4000:]


def test_baseline_passes_all_required_stages(
    check: Callable[..., object], project_copy: Path
) -> None:
    result = check()
    assert result.returncode == 0, result.stdout + result.stderr
    for stage in (
        "config",
        "format",
        "lint",
        "types",
        "docs",
        "architecture",
        "dependencies",
        "secrets",
        "tests",
    ):
        assert_stage(result, stage, "PASS")
    assert any(line.startswith("SKIP online.vulnerabilities") for line in stage_lines(result))


def test_format_violation(check: Callable[..., object], project_copy: Path) -> None:
    _append(project_copy, CORE, "\ndef badly_formatted( ):\n    return 1\n")
    result = check()
    _assert_failure(result, "format", "reformatted")


def test_lint_unused_import(check: Callable[..., object], project_copy: Path) -> None:
    _add_import(project_copy, CORE, "import os")
    result = check()
    _assert_failure(result, "lint", "F401")


def test_cyclomatic_complexity(check: Callable[..., object], project_copy: Path) -> None:
    branches = "\n".join(f"    if value == {index}:\n        return {index}" for index in range(13))
    _append(
        project_copy,
        CORE,
        f'\n\ndef complex_value(value: int) -> int:\n    """Return a value by branch."""\n'
        f"{branches}\n    return -1\n",
    )
    result = check()
    _assert_failure(result, "lint", "C901")


def test_suppression_code_required(check: Callable[..., object], project_copy: Path) -> None:
    _append(
        project_copy,
        CORE,
        "def suppressed() -> None:\n"
        '    """Use a blanket suppression."""\n'
        '    value: int = "wrong"  # type: ignore\n'
        "    _ = value\n",
    )
    result = check()
    _assert_failure(result, "lint", "PGH003")


def test_security_eval_rule(check: Callable[..., object], project_copy: Path) -> None:
    _append(project_copy, CORE, '\nresult = eval("1 + 1")\n')
    result = check()
    _assert_failure(result, "lint", "S307")


def test_docstring_formatting_rule(check: Callable[..., object], project_copy: Path) -> None:
    _append(
        project_copy,
        CORE,
        '\n\ndef format_example() -> None:\n    """Summary without a blank line.\n'
        '    More text.\n    """\n',
    )
    result = check()
    _assert_failure(result, "lint", "D205")


def test_typing_return_violation(check: Callable[..., object], project_copy: Path) -> None:
    _replace(
        project_copy,
        CORE,
        'return f"Hello, {normalized}!"',
        "return 1",
    )
    result = check()
    _assert_failure(result, "types", "Incompatible return value type")


def test_unused_type_ignore(check: Callable[..., object], project_copy: Path) -> None:
    _append(
        project_copy,
        CORE,
        "\nignored: int = 1  # type: ignore[assignment]\n",
    )
    result = check()
    _assert_failure(result, "types", "Unused")


def test_redundant_cast(check: Callable[..., object], project_copy: Path) -> None:
    _add_import(project_copy, CORE, "from typing import cast")
    _append(project_copy, CORE, "\ncast_value = cast(int, 1)\n")
    result = check()
    _assert_failure(result, "types", "Redundant cast")


def test_implicit_optional(check: Callable[..., object], project_copy: Path) -> None:
    _append(
        project_copy,
        CORE,
        '\n\ndef optional_value(value: str = None) -> None:\n    """Accept an optional value."""\n',
    )
    result = check()
    _assert_failure(result, "types", "Incompatible default")


def test_explicit_any_under_strict_flag(check: Callable[..., object], project_copy: Path) -> None:
    _append(
        project_copy,
        ".ai-python/config/mypy.ini",
        "disallow_any_explicit = True\n",
    )
    _add_import(project_copy, CORE, "from typing import Any")
    _append(
        project_copy,
        CORE,
        '\n\ndef passthrough(value: Any) -> Any:\n    """Return the value."""\n    return value\n',
    )
    result = check()
    _assert_failure(result, "types", "Explicit")


def test_missing_docstring_in_custom_test_scope(
    check: Callable[..., object], project_copy: Path
) -> None:
    _replace(
        project_copy,
        ".ai-python/policy.toml",
        'scope = "public"',
        'scope = "custom"',
    )
    _replace(
        project_copy,
        ".ai-python/policy.toml",
        "categories = []",
        'categories = ["tests"]',
    )
    _replace(
        project_copy,
        TESTS,
        '"""Behavior tests for the public greeting API."""\n\n',
        "",
    )
    result = check()
    _assert_failure(result, "docs", "missing module docstring")


def test_missing_structured_return_section(
    check: Callable[..., object], project_copy: Path
) -> None:
    _replace(
        project_copy,
        CORE,
        "    Returns:\n        A greeting in the form ``Hello, <name>!``.\n\n",
        "",
    )
    result = check()
    _assert_failure(result, "docs", "DOC201")


def test_forbidden_architecture_import(check: Callable[..., object], project_copy: Path) -> None:
    (project_copy / "src/example/cli.py").write_text(
        '"""Command module."""\n\n\n'
        'def render() -> str:\n    """Render a command."""\n    return "command"\n',
        encoding="utf-8",
    )
    _replace(
        project_copy,
        ".ai-python/policy.toml",
        'graph = "flat"',
        'graph = "contracts"',
    )
    with (project_copy / ".ai-python/config/importlinter.ini").open(
        "a", encoding="utf-8"
    ) as handle:
        handle.write(
            "\n[importlinter:contract:direction]\n"
            "name = Core direction\n"
            "type = forbidden\n"
            "source_modules =\n    example.core\n"
            "forbidden_modules =\n    example.cli\n"
        )
    _replace(
        project_copy,
        CORE,
        "from __future__ import annotations\n",
        "from __future__ import annotations\n\nfrom example.cli import render\n",
    )
    _append(project_copy, CORE, "\nCOMMAND = render()\n")
    result = check()
    _assert_failure(result, "architecture", "BROKEN")


def test_missing_dependency(check: Callable[..., object], project_copy: Path) -> None:
    _add_import(project_copy, CORE, "import numpy  # type: ignore[import-not-found]")
    _append(project_copy, CORE, "\nNUMPY_NAME = numpy.__name__\n")
    result = check()
    _assert_failure(result, "dependencies", "DEP001")


def test_unused_dependency(check: Callable[..., object], project_copy: Path) -> None:
    _replace(
        project_copy,
        "pyproject.toml",
        "dependencies = []",
        'dependencies = ["typing-extensions==4.16.0"]',
    )
    lock = run(["uv", "lock", "--offline"], cwd=project_copy, env=tool_env())
    assert lock.returncode == 0, lock.stdout + lock.stderr
    result = check()
    _assert_failure(result, "dependencies", "DEP002")


def test_development_only_dependency_import(
    check: Callable[..., object], project_copy: Path
) -> None:
    _add_import(project_copy, CORE, "import pytest")
    _append(project_copy, CORE, "\nPYTEST_NAME = pytest.__name__\n")
    result = check()
    _assert_failure(result, "dependencies", "DEP004")


def test_transitive_dependency_import(check: Callable[..., object], project_copy: Path) -> None:
    _replace(
        project_copy,
        "pyproject.toml",
        "dependencies = []",
        'dependencies = ["requests==2.34.2"]',
    )
    lock = run(["uv", "lock", "--offline"], cwd=project_copy, env=tool_env())
    assert lock.returncode == 0, lock.stdout + lock.stderr
    _add_import(project_copy, CORE, "import urllib3")
    _append(project_copy, CORE, "\nURLLIB3_NAME = urllib3.__name__\n")
    result = check()
    _assert_failure(result, "dependencies", "DEP003")


def test_socket_creation_is_denied(check: Callable[..., object], project_copy: Path) -> None:
    (project_copy / "tests/test_network.py").write_text(
        '"""Network test."""\n\nimport socket\n\n\ndef test_network() -> None:\n'
        '    socket.create_connection(("127.0.0.1", 9), timeout=0.1)\n',
        encoding="utf-8",
    )
    result = check()
    _assert_failure(result, "tests", "tried to use socket")


def test_empty_test_selection_fails(check: Callable[..., object], project_copy: Path) -> None:
    _replace(
        project_copy,
        ".ai-python/policy.toml",
        'categories = ["unit", "regression"]',
        'categories = ["integration"]',
    )
    result = check()
    _assert_failure(result, "tests", "FAIL tests")


def test_selected_integration_category_runs(
    check: Callable[..., object], project_copy: Path
) -> None:
    (project_copy / "tests/test_integration.py").write_text(
        '"""Integration category."""\n\nfrom __future__ import annotations\n\n'
        "import pytest\n\nfrom example import greet\n\n"
        "pytestmark = pytest.mark.integration\n\n\n"
        "def test_category_runs() -> None:\n"
        '    assert greet("World") == "Hello, World!"\n',
        encoding="utf-8",
    )
    _replace(
        project_copy,
        ".ai-python/policy.toml",
        'categories = ["unit", "regression"]',
        'categories = ["integration"]',
    )
    result = check()
    assert result.returncode == 0, result.stdout + result.stderr
    assert_stage(result, "tests", "PASS")
    assert "1 passed" in result.stdout + result.stderr


def test_scoped_baseline_passes_and_fresh_violation_fails(
    check: Callable[..., object], project_copy: Path
) -> None:
    _append(
        project_copy,
        CORE,
        "def approved_secret() -> str:\n"
        '    """Return a legacy fixture value."""\n'
        '    password = "hunter2"  # noqa: S105\n'
        "    return password\n",
    )
    _append(
        project_copy,
        TESTS,
        "def test_approved_secret() -> None:\n"
        "    from example.core import approved_secret\n\n"
        '    assert approved_secret() == "hunter2"\n',
    )
    with (project_copy / ".ai-python/policy.toml").open("a", encoding="utf-8") as handle:
        handle.write(
            """
[[exceptions]]
id = "legacy-s105"
rule = "ruff.S105"
target = "src/example/core.py:approved_secret"
reason = "Legacy fixture retained for the adoption baseline."
owner = "platform-team"
approved_by = "maintainer"
approved_on = "2026-11-20"
expires_on = "2027-11-20"
approval_ref = "https://example.invalid/decisions/1"
"""
        )
    baseline = check()
    assert baseline.returncode == 0, baseline.stdout + baseline.stderr
    assert_stage(baseline, "lint", "PASS")

    _append(
        project_copy,
        CORE,
        'def fresh_secret() -> str:\n    """Return a fresh value."""\n'
        '    password = "hunter3"\n    return password\n',
    )
    result = check()
    _assert_failure(result, "lint", "S105")


def test_coverage_threshold_failure(check: Callable[..., object], project_copy: Path) -> None:
    _replace(
        project_copy,
        ".ai-python/config/coverage.ini",
        "fail_under = 80",
        "fail_under = 100",
    )
    _append(
        project_copy,
        CORE,
        '\n\ndef uncovered(value: int) -> int:\n    """Return a branch value."""\n'
        "    if value > 0:\n        return 1\n    return 0\n",
    )
    result = check()
    _assert_failure(result, "tests", "Coverage failure")


def test_stale_lock_fails_before_format(check: Callable[..., object], project_copy: Path) -> None:
    _replace(
        project_copy,
        "pyproject.toml",
        "dependencies = []",
        'dependencies = ["typing-extensions==4.16.0"]',
    )
    result = check()
    _assert_failure(result, "config", "lockfile")
    assert any(line == "NOT EXECUTED format" for line in stage_lines(result))


def test_missing_lock_fails_configuration(check: Callable[..., object], project_copy: Path) -> None:
    (project_copy / "uv.lock").unlink()
    result = check()
    _assert_failure(result, "config", "lock")


def test_gitleaks_detects_synthetic_secret(
    check: Callable[..., object], project_copy: Path
) -> None:
    (project_copy / "docs").mkdir(exist_ok=True)
    (project_copy / "docs/notes.md").write_text(
        'AWS_ACCESS_KEY_ID = "AKIAIMNOJVGFDXXXE4OA"\n', encoding="utf-8"
    )
    result = check()
    _assert_failure(result, "secrets", "leaks found")


def test_gitleaks_respects_ignored_evidence_path(
    check: Callable[..., object], project_copy: Path
) -> None:
    evidence = project_copy / ".ai-python/evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "leak.txt").write_text(
        'AWS_ACCESS_KEY_ID = "AKIAIMNOJVGFDXXXE4OA"\n', encoding="utf-8"
    )
    result = check()
    assert result.returncode == 0, result.stdout + result.stderr
    assert_stage(result, "secrets", "PASS")


def test_broken_gitleaks_executable_fails_secrets_stage(
    check: Callable[..., object], project_copy: Path, tmp_path: Path
) -> None:
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fake = fake_bin / "gitleaks"
    fake.write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8")
    fake.chmod(0o755)
    base_path = tool_env()["PATH"]
    result = check(env={"PATH": f"{fake_bin}{os.pathsep}{base_path}"})
    _assert_failure(result, "secrets", "FAIL secrets")


def test_missing_gitleaks_executable_fails_secrets_stage(
    check: Callable[..., object], project_copy: Path, tmp_path: Path
) -> None:
    tools = tmp_path / "minimal-bin"
    tools.mkdir()
    for name in ("uv", "bash", "cat", "mkdir"):
        source = shutil.which(name)
        assert source is not None, name
        (tools / name).symlink_to(source)
    result = check(env={"PATH": str(tools)})
    _assert_failure(result, "secrets", "FAIL secrets")
    assert any(line == "NOT EXECUTED tests" for line in stage_lines(result))


@pytest.mark.network
def test_online_mode_runs_live_vulnerability_gate(
    check: Callable[..., object], project_copy: Path
) -> None:
    result = check("online")
    assert result.returncode == 0, result.stdout + result.stderr
    assert_stage(result, "online", "PASS")
