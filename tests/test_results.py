"""Interpretation of JUnit, audit, and pytest selector results."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest


def _policy(adapter: Any, tmp_path: Path, categories: list[str]) -> Any:
    data = {
        "testing": {
            "categories": categories,
            "plugins": [],
        }
    }
    return adapter.Policy(root=tmp_path, data=data, today=date(2026, 11, 24))


def test_junit_accepts_executed_tests(adapter: Any, tmp_path: Path) -> None:
    report = tmp_path / "junit.xml"
    report.write_text(
        '<testsuite tests="2"><testcase name="a"/><testcase name="b"/></testsuite>',
        encoding="utf-8",
    )
    assert adapter.junit_failures(report) == []


def test_junit_rejects_empty_and_all_skipped(adapter: Any, tmp_path: Path) -> None:
    empty = tmp_path / "empty.xml"
    empty.write_text('<testsuite tests="0"></testsuite>', encoding="utf-8")
    assert "collected no tests" in adapter.junit_failures(empty)[0]
    skipped = tmp_path / "skipped.xml"
    skipped.write_text(
        '<testsuite tests="1"><testcase name="a"><skipped/></testcase></testsuite>',
        encoding="utf-8",
    )
    assert "zero tests executed" in adapter.junit_failures(skipped)[0]


def test_junit_rejects_malformed_report(adapter: Any, tmp_path: Path) -> None:
    report = tmp_path / "broken.xml"
    report.write_text("<testsuite>", encoding="utf-8")
    assert "cannot read" in adapter.junit_failures(report)[0]


def test_audit_clean_report_passes(adapter: Any, tmp_path: Path) -> None:
    report = tmp_path / "audit.json"
    report.write_text(json.dumps({"dependencies": [{"name": "a", "version": "1", "vulns": []}]}))
    assert adapter.audit_failures(report) == []


def test_audit_vulnerability_fails(adapter: Any, tmp_path: Path) -> None:
    report = tmp_path / "audit.json"
    report.write_text(
        json.dumps({"dependencies": [{"name": "a", "version": "1", "vulns": [{"id": "GHSA-1"}]}]})
    )
    problems = adapter.audit_failures(report)
    assert any("GHSA-1" in item for item in problems)


def test_audit_skipped_or_unavailable_data_fails(adapter: Any, tmp_path: Path) -> None:
    skipped = tmp_path / "skipped.json"
    skipped.write_text(
        json.dumps({"dependencies": [{"name": "a", "version": "1", "skip_reason": "no provider"}]})
    )
    assert any("skipped" in item for item in adapter.audit_failures(skipped))
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{not json")
    assert any("cannot read" in item for item in adapter.audit_failures(malformed))
    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"dependencies": []}))
    assert adapter.audit_failures(empty) == []


def test_pytest_selector_defaults_include_unit_regression_and_unmarked(
    adapter: Any, tmp_path: Path
) -> None:
    selector = adapter.pytest_selector(_policy(adapter, tmp_path, ["unit", "regression"]))
    assert "unit" in selector
    assert "regression" in selector
    assert "not integration" in selector
    assert "not property" in selector
    assert "not end_to_end" in selector
    assert "not external" in selector
    assert "not stochastic" in selector
    assert "not performance" in selector


def test_pytest_selector_without_unit_excludes_unmarked(adapter: Any, tmp_path: Path) -> None:
    selector = adapter.pytest_selector(_policy(adapter, tmp_path, ["regression"]))
    assert "regression" in selector
    assert "not integration" not in selector


def test_pytest_selector_rejects_empty_categories(adapter: Any, tmp_path: Path) -> None:
    with pytest.raises(Exception, match="must not be empty"):
        adapter.pytest_selector(_policy(adapter, tmp_path, []))
