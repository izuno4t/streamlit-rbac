# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

streamlit-rbac is a lightweight RBAC (Role-Based Access Control) library for Streamlit applications. It provides stateless role-checking functions, a decorator for declarative access control, and optional Streamlit session integration. Core functions have zero dependencies; Streamlit is an optional dependency.

## Development Commands

```bash
# Setup
uv sync --extra dev          # Install all dependencies including dev

# Testing
uv run pytest                # Run all tests
uv run pytest --cov          # Run tests with coverage (target: 90%+)
uv run pytest tests/test_core.py              # Run single test file
uv run pytest tests/test_core.py::TestHasRole # Run single test class
uv run pytest -k "test_name"                  # Run tests matching pattern

# Linting & Formatting
uv run ruff check .          # Lint
uv run ruff check --fix .    # Lint with auto-fix
uv run ruff format .         # Format

# Type Checking
uv run mypy .                # Type check (strict mode enabled)

# Run all checks at once
make check                   # Runs lint, typecheck, test sequentially

# Markdown linting
markdownlint-cli2 "**/*.md"
```

## Architecture

Three-layer architecture with downward-only dependencies:

```
Streamlit Integration (_streamlit.py)  ← depends on streamlit (optional)
  authorize_page()

Decorator (_decorators.py)             ← depends on core only
  @require_roles()

Core (_core.py)                        ← zero dependencies (pure functions)
  has_role(), has_any_role(), has_all_roles(), _resolve_roles()
```

- **_types.py** — Type aliases: `RoleLoader`, `OnDeniedHandler`
- **_exceptions.py** — Empty placeholder for future custom exceptions
- **__init__.py** — Re-exports core/decorator/types; uses PEP 562 `__getattr__` for lazy-loading Streamlit functions (so `import streamlit` is deferred until actual use)

All internal modules are prefixed with `_`. Users import from `streamlit_rbac` directly.

## Key Design Decisions

- `user_roles` and `role_loader` are mutually exclusive keyword-only params (ValueError if both or neither)
- Roles are case-sensitive strings
- `_resolve_roles()` returns `frozenset` for set-operation efficiency
- `@require_roles` uses OR logic; always raises `PermissionError` (even after `on_denied` callback)
- `authorize_page()` never raises — uses `st.error()` + `st.stop()` instead
- Streamlit is imported inside functions, not at module level (optional dependency pattern)
- `ParamSpec`/`TypeVar` preserve decorated function signatures for mypy strict

## Configuration

- Python: >=3.11 (pyproject.toml), strict mypy
- Ruff rules: E, W, F, I, B, C4, UP, ARG, SIM, TCH, PTH, ERA, PL, RUF (E501 ignored)
- Build: hatchling with src layout (`src/streamlit_rbac/`)

## Specifications

Detailed requirements, API spec, and internal design are in `docs/`:
- `docs/REQUIREMENTS.md` — 8 functional requirements (REQ-1 through REQ-8)
- `docs/SPECIFICATION.md` — External API behavior and integration scenarios
- `docs/DESIGN.md` — Internal module design with reference implementations and test examples
