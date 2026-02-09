"""Home page."""

import streamlit as st

st.title("streamlit-rbac デモ")
st.write("サイドバーでユーザーを切り替えて、各ページの表示制御を確認してください。")

st.header("公開ページ")
st.write("このページはロールに関係なく誰でも閲覧できます。")
