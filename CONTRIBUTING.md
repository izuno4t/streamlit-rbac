# Contributing

## Setup

```bash
git clone https://github.com/izuno4t/streamlit-rbac.git
cd streamlit-rbac
uv sync --all-extras
```

## Tests

```bash
uv run pytest --cov
```

## Lint & Type Check

```bash
uv run ruff check src tests
uv run mypy src
```
