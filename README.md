# streamlit-rbac

Lightweight Role-Based Access Control (RBAC) library for Streamlit applications.

Inspired by Spring Security's authorization API,
`streamlit-rbac` provides a thin, declarative layer for role-based access control
— without pulling in authentication, user management, or any heavyweight framework.

## Features

- **Pure function core** — `has_role()`, `has_any_role()`, `has_all_roles()` are stateless
  and side-effect-free, making them trivial to unit test.
- **Declarative decorator** — `@require_roles()` guards functions with a single line.
- **Streamlit integration** — `authorize_page()` stops unauthorized page rendering via `st.stop()`.
- **Bring your own auth** — inject any `role_loader` function to resolve roles
  from IdP tokens, session state, databases, or anything else.
- **Zero required dependencies** — core functions use only the Python standard library. Streamlit is an optional dependency.

## Installation

```bash
pip install streamlit-rbac

# With Streamlit integration
pip install streamlit-rbac[streamlit]
```

> **Requires Python 3.11+**

## Quick Start

### Pure functions (great for testing)

```python
from streamlit_rbac import has_role, has_any_role, has_all_roles

# Single role check
has_role("Admin", user_roles=["Admin", "User"])  # True
has_role("Admin", user_roles=["User"])            # False

# Any of these roles (OR)
has_any_role("Admin", "Manager", user_roles=["Manager"])  # True

# All of these roles (AND)
has_all_roles("Admin", "Auditor", user_roles=["Admin", "Auditor"])  # True
has_all_roles("Admin", "Auditor", user_roles=["Admin"])              # False
```

### Role loader (deferred evaluation)

Instead of passing roles directly, supply a callable that returns them:

```python
from streamlit_rbac import has_role

def get_user_roles() -> list[str]:
    # Fetch from IdP, database, session, etc.
    return ["Admin", "User"]

has_role("Admin", role_loader=get_user_roles)  # True
```

> `user_roles` and `role_loader` are mutually exclusive — pass one or the other, never both.

### Decorator

```python
from streamlit_rbac import require_roles

@require_roles("Admin", role_loader=get_user_roles)
def delete_user(user_id: str) -> None:
    ...
```

Raises `PermissionError` if the user lacks the required role. An optional `on_denied` callback runs before the error:

```python
@require_roles("Admin", role_loader=get_user_roles, on_denied=log_violation)
def delete_user(user_id: str) -> None:
    ...
```

### Streamlit page guard

```python
import streamlit as st
from streamlit_rbac import authorize_page

def get_user_roles() -> list[str]:
    claims = st.session_state.get("token_claims", {})
    return claims.get("roles", [])

# Place at the top of each page script
authorize_page("Admin", role_loader=get_user_roles)

st.title("Admin Page")  # Only rendered if authorized
```

If the user lacks the required role, `authorize_page` displays an error message
and calls `st.stop()` — nothing below it executes.

## Component-Level Control

Mix page guards with inline checks for fine-grained control:

```python
from streamlit_rbac import authorize_page, has_role

authorize_page("User", "Admin", role_loader=get_user_roles)
st.title("Dashboard")

# Only SuperAdmins see this section
if has_role("SuperAdmin", role_loader=get_user_roles):
    with st.expander("System Settings"):
        st.write("Dangerous operations...")
```

## API Reference

### Core Functions

| Function | Description |
| -------- | ----------- |
| `has_role(required, *, user_roles=None, role_loader=None)` | Check for a single role |
| `has_any_role(*required, *, user_roles=None, role_loader=None)` | Check for any of the given roles (OR) |
| `has_all_roles(*required, *, user_roles=None, role_loader=None)` | Check for all of the given roles (AND) |

All return `bool`. All raise `ValueError` if both or neither of `user_roles` / `role_loader` are provided.

**Edge cases:** `has_any_role()` with no required roles returns `False`.
`has_all_roles()` with no required roles returns `True` (vacuous truth).

### Decorator API

| Function | Description |
| -------- | ----------- |
| `@require_roles(*roles, *, user_roles=None, role_loader=None, on_denied=None)` | Guard a function (OR logic). Raises `PermissionError` on denial. |

### Streamlit Integration

| Function | Description |
| -------- | ----------- |
| `authorize_page(*roles, *, role_loader, login_url=None, denied_message=...)` | Page-level guard. Calls `st.stop()` on denial. |

### Types

| Type | Definition |
| ---- | ---------- |
| `RoleLoader` | `Callable[[], Iterable[str]]` |
| `OnDeniedHandler` | `Callable[[], None]` |

## Design Principles

**Authorization only.**
No authentication, no user management, no database schemas.
This library answers one question: *does this user have the required role?*

**Developer stays in control.**
Role resolution is entirely your responsibility via `role_loader`.
The library never dictates where roles come from.

**Pure core, optional integration.**
Core functions have zero dependencies.
Streamlit is only imported when you use `authorize_page()`.

**Spring Security heritage, Pythonic API.**
Familiar concepts (`hasRole` → `has_role`, `@PreAuthorize` → `@require_roles`),
expressed with keyword-only arguments, type hints, and decorators.

## Development

```bash
# Clone and install
git clone https://github.com/your-org/streamlit-rbac.git
cd streamlit-rbac
uv sync --all-extras

# Run tests
uv run pytest --cov

# Lint and type check
uv run ruff check src tests
uv run mypy src
```

## License

MIT
