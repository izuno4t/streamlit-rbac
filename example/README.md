# streamlit-rbac Example

A multi-page Streamlit application demonstrating role-based access control with `streamlit-rbac`.

## Getting Started

From the project root:

```bash
uv run streamlit run example/app.py
```

A browser window will open. Use the sidebar to switch users and observe how access control behaves on each page.

## File Structure

```text
example/
  app.py            Entry point. Builds navigation dynamically based on roles
  common.py         Shared module: role definitions, users, role loader
  pages/
    Home.py         Public page (no authorization required)
    User.py         Accessible by User / Manager / Admin
    Manager.py      Accessible by Manager / Admin
    Admin.py        Accessible by Admin only
```

## Integration Guide

### 1. Define a role loader

`streamlit-rbac` does not dictate how roles are retrieved.
Implement a function matching `RoleLoader` (`Callable[[], Iterable[str]]`) and pass it as the `role_loader` argument.

```python
# common.py
def get_user_roles() -> list[str]:
    return st.session_state.get("user_roles", [])
```

The source can be session state, a database, an IdP token, or anything else.

### 2. Hide navigation links by role

Build the `st.navigation` page list dynamically so that unauthorized users never see links they cannot access.

```python
# app.py
from streamlit_rbac import has_role

pages = [
    st.Page("pages/Home.py", title="Home", default=True),
    st.Page("pages/User.py", title="User"),
    st.Page("pages/Manager.py", title="Manager"),
]

if has_role("Admin", role_loader=get_user_roles):
    pages.append(st.Page("pages/Admin.py", title="Admin"))

pg = st.navigation(pages)
pg.run()
```

This keeps the sidebar clean: users only see pages they are allowed to visit.

### 3. Guard pages with `authorize_page()`

Even when navigation links are hidden, users can still reach a page by entering its URL directly.
Call `authorize_page()` at the top of each page script as a fallback guard.

```python
# pages/Admin.py
from streamlit_rbac import authorize_page

authorize_page("Admin", role_loader=get_user_roles)

st.header("Admin Page")  # Only reached if authorized
```

Combine step 2 and step 3 for defense in depth: navigation hides the link, `authorize_page()` blocks direct access.

### 4. Control individual components with `has_role()` / `has_any_role()`

For fine-grained control within a page, use the core functions to conditionally render sections.

```python
# pages/User.py
from streamlit_rbac import has_any_role

if has_any_role("Manager", "Admin", role_loader=get_user_roles):
    st.subheader("Detailed Report (Manager / Admin only)")
```

### 5. Use an Enum for role identifiers

Define a `Role` enum to avoid scattered string literals. Pass `.value` to library functions.

```python
from enum import Enum

class Role(Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    USER = "User"

authorize_page(Role.ADMIN.value, role_loader=get_user_roles)
```

## Demo Users

| User | Roles |
| --- | --- |
| alice (Admin) | Admin, User |
| bob (Manager) | Manager, User |
| charlie (User) | User |
| guest | (none) |

Switch users in the sidebar to see how navigation links, page access, and component visibility change.
