"""デモアプリ共通モジュール.

ロール定義・ユーザー定義・ロールローダー・サイドバー描画を提供する。
"""

from enum import Enum

import streamlit as st


class Role(Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    USER = "User"


USERS: dict[str, list[str]] = {
    "alice (Admin)": [Role.ADMIN.value, Role.USER.value],
    "bob (Manager)": [Role.MANAGER.value, Role.USER.value],
    "charlie (User)": [Role.USER.value],
    "guest (未ログイン)": [],
}


def get_user_roles() -> list[str]:
    """st.session_state からロール一覧を取得する."""
    return st.session_state.get("user_roles", [])


def setup_sidebar() -> str:
    """サイドバーにユーザー切り替えUIを描画し、選択中のユーザー名を返す."""
    st.sidebar.title("Demo: ユーザー切り替え")

    selected_user = st.sidebar.selectbox("ユーザーを選択", list(USERS.keys()))
    st.session_state["user_roles"] = USERS[selected_user]

    st.sidebar.divider()
    st.sidebar.write("**現在のロール:**")
    roles = st.session_state["user_roles"]
    if roles:
        for role in roles:
            st.sidebar.write(f"- {role}")
    else:
        st.sidebar.write("_(ロールなし)_")

    return selected_user
