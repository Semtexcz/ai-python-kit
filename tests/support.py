"""Shared constants and helpers for the AI Python Kit tests."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = KIT_ROOT / "template/.ai-python/kit/adapter/ai_python_policy.py"
TODAY = date(2026, 11, 24)
NATIVE_CONFIGS = (
    "ruff.toml",
    "mypy.ini",
    "flake8.ini",
    "importlinter.ini",
    "gitleaks.toml",
    "pytest.ini",
    "coverage.ini",
)
VERIFICATION_COMMAND = "just --justfile .ai-python/kit/justfile"


def run(
    command: Sequence[str | Path],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int = 300,
) -> subprocess.CompletedProcess[str]:
    """Run a command with captured output."""
    merged = os.environ.copy()
    merged.update(env or {})
    merged["UV_LINK_MODE"] = "copy"
    return subprocess.run(
        [str(item) for item in command],
        cwd=cwd,
        text=True,
        capture_output=True,
        env=merged,
        timeout=timeout,
        check=False,
    )


def tool_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Return a PATH with the kit tool environment first."""
    values = {
        "PATH": f"{Path(sys.executable).parent}{os.pathsep}{os.environ.get('PATH', '')}",
        "UV_LINK_MODE": "copy",
    }
    values.update(extra or {})
    return values


def copier_copy(destination: Path, **answers: object) -> Path:
    """Render the kit template into a destination directory."""
    command: list[str] = [sys.executable, "-m", "copier", "copy", "--defaults"]
    for key, value in answers.items():
        command.extend(["-d", f"{key}={value}"])
    command.extend([str(KIT_ROOT), str(destination)])
    result = run(command, cwd=destination.parent)
    if result.returncode != 0:
        raise AssertionError(f"copier copy failed:\n{result.stdout}\n{result.stderr}")
    return destination


def write_full_project(
    root: Path,
    *,
    policy: str,
    pyproject: str,
    package: str = "example",
    source_files: dict[str, str] | None = None,
) -> Path:
    """Create a minimal valid project layout for adapter unit tests."""
    (root / ".ai-python/config").mkdir(parents=True)
    for name in NATIVE_CONFIGS:
        (root / ".ai-python/config" / name).write_text("\n", encoding="utf-8")
    (root / ".ai-python/policy.toml").write_text(policy, encoding="utf-8")
    (root / ".copier-answers.ai-python-kit.yml").write_text("schema: 1\n", encoding="utf-8")
    (root / "AGENTS.md").write_text(VERIFICATION_COMMAND + "\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    (root / "docs").mkdir()
    (root / "docs/architecture.md").write_text("Boundary.\n", encoding="utf-8")
    package_dir = root / "src" / package
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text('"""Package."""\n', encoding="utf-8")
    for relative, content in (source_files or {"core.py": '"""Core."""\n'}).items():
        path = package_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests/test_smoke.py").write_text(
        '"""Tests."""\n\n\ndef test_smoke() -> None:\n    assert True\n',
        encoding="utf-8",
    )
    return root


def base_policy(**overrides: str) -> str:
    """Return a policy document with selected values."""
    values = {
        "profiles": '["library"]',
        "quality": "standard",
        "style": "modular",
        "graph": "flat",
        "runtime": "balanced",
        "development": "reuse-first",
        "docstring_scope": "public",
        "categories": "[]",
        "test_categories": '["unit", "regression"]',
        "plugins": "[]",
        "verify_groups": "[]",
        "verify_extras": "[]",
        "extra": "",
    }
    values.update(overrides)
    return f"""schema = 1
profiles = {values["profiles"]}
quality = "{values["quality"]}"

[project]
package = "example"
source = ["src"]
tests = ["tests"]
verify_groups = {values["verify_groups"]}
verify_extras = {values["verify_extras"]}

[architecture]
style = "{values["style"]}"
reference = "docs/architecture.md"
graph = "{values["graph"]}"

[dependencies]
runtime = "{values["runtime"]}"
development = "{values["development"]}"
approve_runtime_additions = true
approve_development_additions = false

[typing]
annotation_scope = "production"
scope_reference = ""

[docstrings]
format = "google"
scope = "{values["docstring_scope"]}"
public_detail = "standard"
private_detail = "summary"
language = "en"
categories = {values["categories"]}

[testing]
categories = {values["test_categories"]}
plugins = {values["plugins"]}

[review]
function_lines = 60
module_lines = 400
{values["extra"]}"""


DEFAULT_PYPROJECT = """\
[build-system]
requires = ["uv_build==0.13.9"]
build-backend = "uv_build"

[project]
name = "example-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
ai-python-kit = [
    "coverage==7.17.5",
    "deptry==0.25.1",
    "flake8==7.5.0",
    "import-linter==2.17",
    "mypy==2.4.1",
    "packaging==26.4",
    "pip-audit==2.10.1",
    "pydoclint==0.12.0",
    "pytest==9.2.0",
    "pytest-socket==0.8.1",
    "ruff==0.17.6",
]
dev = []

[tool.uv.build-backend]
module-name = "example"
module-root = "src"
"""


def stage_lines(result: subprocess.CompletedProcess[str]) -> list[str]:
    """Return the compact per-stage result lines from check output."""
    return [
        line
        for line in result.stdout.splitlines()
        if line.startswith(("PASS ", "FAIL ", "SKIP ", "NOT EXECUTED "))
    ]


def assert_stage(result: subprocess.CompletedProcess[str], stage: str, outcome: str) -> None:
    """Assert that a stage reported the expected outcome."""
    expected = f"{outcome} {stage}"
    lines = stage_lines(result)
    assert any(line.startswith(expected) for line in lines), (
        f"expected '{expected}' in stages:\n" + "\n".join(lines) + "\n\n" + result.stdout[-3000:]
    )
