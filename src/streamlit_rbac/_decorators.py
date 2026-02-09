"""streamlit-rbac のデコレータ."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from streamlit_rbac._core import has_any_role

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from streamlit_rbac._types import OnDeniedHandler, RoleLoader

P = ParamSpec("P")
R = TypeVar("R")


def require_roles(
    *allowed_roles: str,
    user_roles: Iterable[str] | None = None,
    role_loader: RoleLoader | None = None,
    on_denied: OnDeniedHandler | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """関数実行前にロールチェックを行うデコレータ."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if not has_any_role(
                *allowed_roles,
                user_roles=user_roles,
                role_loader=role_loader,
            ):
                if on_denied is not None:
                    on_denied()
                msg = f"Access denied: required one of {allowed_roles}"
                raise PermissionError(msg)
            return func(*args, **kwargs)

        return wrapper

    return decorator
