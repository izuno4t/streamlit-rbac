"""Admin ページ."""

import streamlit as st
from common import Role, get_user_roles

from streamlit_rbac import authorize_page

authorize_page(Role.ADMIN.value, role_loader=get_user_roles)

st.header("Admin ページ")
st.write("Admin ロールを持つユーザーのみ閲覧できます。")

st.subheader("システム設定")
st.toggle("メンテナンスモード", value=False)
st.toggle("新規登録の受付", value=True)

st.subheader("監査ログ")
st.dataframe(
    {
        "日時": ["2026-02-09 10:00", "2026-02-09 09:30", "2026-02-09 09:00"],
        "操作": ["ユーザー削除", "ロール変更", "設定変更"],
        "実行者": ["alice", "alice", "alice"],
    }
)
