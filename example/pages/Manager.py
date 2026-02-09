# ruff: noqa: RUF001
"""Manager ページ."""

import streamlit as st
from common import Role, get_user_roles

from streamlit_rbac import authorize_page, has_role, require_roles

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


# @require_roles デコレータの使用例
# Admin ロールがなければ PermissionError が発生し、関数は実行されない
@require_roles(Role.ADMIN.value, role_loader=get_user_roles)
def delete_member(name: str) -> str:
    """Delete a member (Admin only)."""
    return f"{name} を削除しました。"


st.divider()
st.subheader("メンバー削除（Admin のみ）")

if has_role(Role.ADMIN.value, role_loader=get_user_roles):
    target = st.selectbox("削除対象", ["田中", "佐藤", "鈴木"])
    if st.button("削除を実行"):
        try:
            result = delete_member(target)
            st.success(result)
        except PermissionError as e:
            st.error(str(e))
else:
    st.info("メンバー削除の操作には Admin 権限が必要です。")
