# ruff: noqa: RUF001
"""Manager ページ."""

import streamlit as st
from common import Role, get_user_roles

from streamlit_rbac import authorize_page, has_role

authorize_page(Role.MANAGER.value, Role.ADMIN.value, role_loader=get_user_roles)

st.header("Manager ページ")
st.write("Manager / Admin ロールを持つユーザーが閲覧できます。")

st.subheader("チーム管理")
st.dataframe(
    {
        "メンバー": ["田中", "佐藤", "鈴木"],
        "ロール": [Role.USER.value, Role.USER.value, Role.MANAGER.value],
        "ステータス": ["アクティブ", "アクティブ", "アクティブ"],
    }
)

# Admin のみの操作ボタン
if has_role(Role.ADMIN.value, role_loader=get_user_roles):
    st.divider()
    st.subheader("ロール変更（Admin のみ）")
    st.warning("この操作は Admin ロールが必要です。")
    st.button("ロールを変更", disabled=False)
else:
    st.divider()
    st.info("ロール変更の操作には Admin 権限が必要です。")
