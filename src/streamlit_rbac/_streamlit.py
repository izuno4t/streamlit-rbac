"""streamlit-rbac の Streamlit統合.

st.session_state との連携およびページガード機能を提供する。
このモジュールは streamlit パッケージに依存する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from streamlit_rbac._core import has_any_role

if TYPE_CHECKING:
    from streamlit_rbac._types import RoleLoader


def guard_page(
    *allowed_roles: str,
    role_loader: RoleLoader,
    login_url: str | None = None,
    denied_message: str = "このページへのアクセス権限がありません。",
) -> None:
    """ページ先頭でアクセス制御を行う."""
    import streamlit as st  # noqa: PLC0415

    user_roles = list(role_loader())

    if not user_roles:
        if login_url is not None:
            st.warning("ログインが必要です。")
            st.link_button("ログインページへ", login_url)
            st.stop()
            return
        st.error("ログインが必要です。")
        st.stop()
        return

    if not has_any_role(*allowed_roles, user_roles=user_roles):
        st.error(denied_message)
        st.stop()


def session_role_loader(
    session_key: str = "user_roles",
) -> RoleLoader:
    """st.session_state からロール一覧を取得するローダーを生成する."""

    def loader() -> list[str]:
        import streamlit as st  # noqa: PLC0415

        roles = st.session_state.get(session_key, [])
        if not isinstance(roles, (list, tuple, set, frozenset)):
            return []
        return list(roles)

    return loader


def user_attr_role_loader(
    user_session_key: str = "user",
    role_attr: str = "roles",
) -> RoleLoader:
    """st.session_state のユーザーオブジェクトからロールを取得するローダーを生成する."""

    def loader() -> list[str]:
        import streamlit as st  # noqa: PLC0415

        user: Any = st.session_state.get(user_session_key)
        if user is None:
            return []
        roles = getattr(user, role_attr, [])
        if not isinstance(roles, (list, tuple, set, frozenset)):
            return []
        return list(roles)

    return loader
