"""streamlit-rbac の Streamlit統合.

st.session_state との連携およびページガード機能を提供する。
このモジュールは streamlit パッケージに依存する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from streamlit_rbac._core import has_any_role

if TYPE_CHECKING:
    from streamlit_rbac._types import RoleLoader


def authorize_page(
    *allowed_roles: str,
    role_loader: RoleLoader,
    login_url: str | None = None,
    denied_message: str = "このページへのアクセス権限がありません。",
) -> None:
    """ページ先頭でアクセス制御を行う."""
    if not allowed_roles:
        msg = "allowed_roles must not be empty."
        raise ValueError(msg)

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
        return
