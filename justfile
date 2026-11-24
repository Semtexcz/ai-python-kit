set shell := ["bash", "-euo", "pipefail", "-c"]

default:
    @just --list

# Deterministic kit checks without rendered-project or network tests.
check:
    uv run ruff format --check tests template/.ai-python/kit/adapter/ai_python_policy.py
    uv run ruff check tests template/.ai-python/kit/adapter/ai_python_policy.py
    uv run mypy template/.ai-python/kit/adapter/ai_python_policy.py
    uv run pytest -m "not e2e and not network"

# Full local suite including rendered projects and live advisory checks.
check-all:
    uv run ruff format --check tests template/.ai-python/kit/adapter/ai_python_policy.py
    uv run ruff check tests template/.ai-python/kit/adapter/ai_python_policy.py
    uv run mypy template/.ai-python/kit/adapter/ai_python_policy.py
    uv run pytest

# Validate every shipped skill with the pinned reference validator.
validate-skills:
    #!/usr/bin/env bash
    set -euo pipefail
    for skill in template/.ai-python/kit/skills/*/; do
        if [[ -f "${skill}SKILL.md" ]]; then
            skills-ref validate "${skill}"
        fi
    done
