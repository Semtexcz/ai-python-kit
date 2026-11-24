"""Docstring presence behavior of the policy adapter."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest


def _policy(
    adapter: Any,
    root: Path,
    *,
    scope: str = "public",
    categories: list[str] | None = None,
    tests: list[str] | None = None,
) -> Any:
    data = {
        "project": {
            "package": "pkg",
            "source": ["src"],
            "tests": tests or ["tests"],
        },
        "docstrings": {
            "format": "google",
            "scope": scope,
            "public_detail": "standard",
            "private_detail": "summary",
            "language": "en",
            "categories": categories or [],
        },
    }
    return adapter.Policy(root=root, data=data, today=date(2026, 11, 24))


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_public_scope_requires_public_presence_and_accepts_getter_docs(
    adapter: Any, tmp_path: Path
) -> None:
    _write(tmp_path, "src/pkg/__init__.py", '"""Package."""\n')
    _write(
        tmp_path,
        "src/pkg/mod.py",
        '''"""Module."""


class Thing:
    """Thing."""

    @property
    def value(self) -> int:
        """Return a value."""
        return 1

    @value.setter
    def value(self, value: int) -> None:
        pass


def public() -> None:
    """Do something."""


async def _private() -> None:
    pass
''',
    )
    failures, warnings = adapter.missing_docstrings(_policy(adapter, tmp_path))
    assert failures == []
    assert warnings == []


def test_public_scope_reports_missing_async_function(adapter: Any, tmp_path: Path) -> None:
    _write(tmp_path, "src/pkg/__init__.py", '"""Package."""\n')
    _write(tmp_path, "src/pkg/mod.py", '"""Module."""\n\nasync def work() -> None:\n    pass\n')
    failures, _ = adapter.missing_docstrings(_policy(adapter, tmp_path))
    assert len(failures) == 1
    assert "missing function docstring for 'work'" in failures[0]


def test_empty_docstring_is_missing(adapter: Any, tmp_path: Path) -> None:
    _write(tmp_path, "src/pkg/__init__.py", '"""Package."""\n')
    _write(
        tmp_path,
        "src/pkg/mod.py",
        '"""Module."""\n\n\ndef empty() -> None:\n    """"""\n',
    )
    failures, _ = adapter.missing_docstrings(_policy(adapter, tmp_path))
    assert any("empty" in item for item in failures)


def test_all_scope_includes_private_declarations(adapter: Any, tmp_path: Path) -> None:
    _write(tmp_path, "src/pkg/__init__.py", '"""Package."""\n')
    _write(
        tmp_path,
        "src/pkg/mod.py",
        '"""Module."""\n\n\ndef _private() -> None:\n    pass\n\n\nclass _Hidden:\n    pass\n',
    )
    failures, _ = adapter.missing_docstrings(_policy(adapter, tmp_path, scope="all"))
    assert any("_private" in item for item in failures)
    assert any("_Hidden" in item for item in failures)


def test_custom_scope_checks_only_selected_categories(adapter: Any, tmp_path: Path) -> None:
    _write(tmp_path, "src/pkg/__init__.py", '"""Package."""\n')
    _write(
        tmp_path,
        "src/pkg/mod.py",
        '"""Module."""\n\n\ndef public() -> None:\n    pass\n\n\nclass Hidden:\n    pass\n',
    )
    failures, _ = adapter.missing_docstrings(
        _policy(adapter, tmp_path, scope="custom", categories=["classes"])
    )
    assert any("class docstring for 'Hidden'" in item for item in failures)
    assert not any("function docstring" in item for item in failures)
    assert not any("module docstring" in item for item in failures)


def test_custom_tests_category_covers_test_modules_and_functions(
    adapter: Any, tmp_path: Path
) -> None:
    _write(tmp_path, "src/pkg/__init__.py", '"""Package."""\n')
    _write(tmp_path, "src/pkg/mod.py", '"""Module."""\n')
    _write(tmp_path, "tests/test_mod.py", "def test_behavior() -> None:\n    assert True\n")
    failures, _ = adapter.missing_docstrings(
        _policy(adapter, tmp_path, scope="custom", categories=["tests"])
    )
    assert any("module docstring for 'tests/test_mod.py'" in item for item in failures)
    assert any("function docstring for 'test_behavior'" in item for item in failures)
    assert not any("src/pkg" in item for item in failures)


def test_overloads_use_the_concrete_implementation(adapter: Any, tmp_path: Path) -> None:
    _write(tmp_path, "src/pkg/__init__.py", '"""Package."""\n')
    _write(
        tmp_path,
        "src/pkg/mod.py",
        '''"""Module."""

from typing import overload


@overload
def convert(value: int) -> int: ...


@overload
def convert(value: str) -> str: ...


def convert(value: Any) -> Any:
    """Convert a value."""
    return value
''',
    )
    failures, _ = adapter.missing_docstrings(_policy(adapter, tmp_path))
    assert failures == []


def test_dynamic_all_is_reported_for_review(adapter: Any, tmp_path: Path) -> None:
    _write(tmp_path, "src/pkg/__init__.py", '"""Package."""\n')
    _write(
        tmp_path,
        "src/pkg/mod.py",
        '"""Module."""\n\n__all__ = build_all()\n\n\n'
        'def build_all() -> list[str]:\n    """Build names."""\n    return []\n',
    )
    failures, warnings = adapter.missing_docstrings(_policy(adapter, tmp_path))
    assert failures == []
    assert any("dynamic __all__" in warning for warning in warnings)


def test_public_scope_ignores_private_modules(adapter: Any, tmp_path: Path) -> None:
    _write(tmp_path, "src/pkg/__init__.py", '"""Package."""\n')
    _write(tmp_path, "src/pkg/_private.py", "def helper() -> None:\n    pass\n")
    failures, _ = adapter.missing_docstrings(_policy(adapter, tmp_path))
    assert failures == []


@pytest.mark.parametrize("scope", ["public", "all"])
def test_tests_are_opt_in_for_non_custom_scope(adapter: Any, tmp_path: Path, scope: str) -> None:
    _write(tmp_path, "src/pkg/__init__.py", '"""Package."""\n')
    _write(tmp_path, "src/pkg/mod.py", '"""Module."""\n')
    _write(tmp_path, "tests/test_mod.py", "def test_behavior() -> None:\n    assert True\n")
    failures, _ = adapter.missing_docstrings(_policy(adapter, tmp_path, scope=scope))
    assert failures == []
