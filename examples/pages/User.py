# ruff: noqa: RUF001
"""User ページ."""

import streamlit as st
from common import Role, get_user_roles

from streamlit_rbac import authorize_page, has_any_role

authorize_page(
    Role.USER.value,
    Role.MANAGER.value,
    Role.ADMIN.value,
    role_loader=get_user_roles,
)

st.header("User ページ")
st.write("User / Manager / Admin ロールを持つユーザーが閲覧できます。")

st.subheader("ダッシュボード")
col1, col2, col3 = st.columns(3)
col1.metric("売上", "¥1,234,567", "+12%")
col2.metric("ユーザー数", "8,432", "+3%")
col3.metric("コンバージョン率", "4.2%", "-0.5%")

# コンポーネント単位の制御
if has_any_role(Role.MANAGER.value, Role.ADMIN.value, role_loader=get_user_roles):
    st.divider()
    st.subheader("詳細レポート（Manager / Admin のみ）")
    st.write("月次レポートのデータがここに表示されます。")
