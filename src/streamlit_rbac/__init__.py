"""streamlit-rbac: Lightweight RBAC library for Streamlit applications."""

from streamlit_rbac._core import has_all_roles, has_any_role, has_role
from streamlit_rbac._decorators import require_roles
from streamlit_rbac._types import OnDeniedHandler, RoleLoader

__all__ = [
    "OnDeniedHandler",
    "RoleLoader",
    "has_all_roles",
    "has_any_role",
    "has_role",
    "require_roles",
]

__version__ = "0.1.0"


def __getattr__(name: str) -> object:
    """Streamlit統合モジュールの遅延import."""
    _streamlit_names = {
        "guard_page",
        "session_role_loader",
        "user_attr_role_loader",
    }
    if name in _streamlit_names:
        from streamlit_rbac import _streamlit  # noqa: PLC0415

        return getattr(_streamlit, name)
    raise AttributeError(f"module 'streamlit_rbac' has no attribute {name!r}")
