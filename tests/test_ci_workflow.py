"""CI example pins, permissions, and parity with the local entry point."""

from __future__ import annotations

from tests.support import KIT_ROOT

WORKFLOW = KIT_ROOT / "template/.github/workflows/ci.yml.jinja"
COMMAND = "just --justfile .ai-python/kit/justfile --working-directory . check"


def _text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_workflow_uses_read_only_permissions_and_pinned_actions() -> None:
    text = _text()
    assert "permissions:\n  contents: read" in text
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in text
    assert "astral-sh/setup-uv@1db35dd8eee11c5894872e0b383ae6c406cf738d" in text
    assert 'UV_VERSION: "0.13.9"' in text
    assert 'JUST_VERSION: "1.59.0"' in text
    assert 'GITLEAKS_VERSION: "8.30.1"' in text


def test_workflow_runs_the_same_local_command_and_online_mode() -> None:
    text = _text()
    assert COMMAND in text
    assert f"{COMMAND} online" in text
    assert "uv lock --check" in text
    assert "uv sync --locked --no-default-groups --group ai-python-kit" in text
    assert "schedule:" in text
    assert "workflow_dispatch:" in text


def test_workflow_has_no_secrets_or_model_calls() -> None:
    text = _text().lower()
    for forbidden in ("openai", "anthropic", "api_key", "secrets.", "model:"):
        assert forbidden not in text


def test_bootstrap_ci_example_matches_the_pins() -> None:
    snippet = (KIT_ROOT / "template/.ai-python/kit/bootstrap/adopt/ci.yml").read_text(
        encoding="utf-8"
    )
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in snippet
    assert "astral-sh/setup-uv@1db35dd8eee11c5894872e0b383ae6c406cf738d" in snippet
    assert COMMAND in snippet
