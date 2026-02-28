"""streamlit-rbac のコア判定関数.

状態を持たない純粋関数としてロールベースのアクセス判定を提供する。
すべての関数は標準ライブラリのみに依存する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from streamlit_rbac._types import RoleLoader


def _resolve_roles(
    user_roles: Iterable[str] | None,
    role_loader: RoleLoader | None,
) -> frozenset[str]:
    """ユーザーロールを解決する内部関数.

    user_roles と role_loader の排他チェックを行い、
    ロール一覧を frozenset として返却する。

    Raises:
        ValueError: 両方が指定された場合、またはどちらも指定されない場合.
    """
    if user_roles is not None and role_loader is not None:
        msg = (
            "user_roles and role_loader are mutually exclusive. "
            "Specify one or the other, not both."
        )
        raise ValueError(msg)
    if user_roles is None and role_loader is None:
        msg = "Either user_roles or role_loader must be specified."
        raise ValueError(msg)

    if user_roles is not None:
        return frozenset(user_roles)

    if role_loader is None:  # pragma: no cover
        msg = "Either user_roles or role_loader must be specified."
        raise ValueError(msg)
    return frozenset(role_loader())


def has_role(
    required: str,
    *,
    user_roles: Iterable[str] | None = None,
    role_loader: RoleLoader | None = None,
) -> bool:
    """指定されたロールを保持しているかを判定する."""
    resolved = _resolve_roles(user_roles, role_loader)
    return required in resolved


def has_any_role(
    *required: str,
    user_roles: Iterable[str] | None = None,
    role_loader: RoleLoader | None = None,
) -> bool:
    """指定されたロールのいずれかを保持しているかを判定する."""
    if not required:
        return False
    resolved = _resolve_roles(user_roles, role_loader)
    return bool(resolved & frozenset(required))


def has_all_roles(
    *required: str,
    user_roles: Iterable[str] | None = None,
    role_loader: RoleLoader | None = None,
) -> bool:
    """指定されたロールのすべてを保持しているかを判定する."""
    if not required:
        return True
    resolved = _resolve_roles(user_roles, role_loader)
    return frozenset(required) <= resolved
