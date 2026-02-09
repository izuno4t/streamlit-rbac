"""streamlit-rbac デモアプリケーション.

サイドバーでユーザーとロールを切り替え、
ページ単位・コンポーネント単位のアクセス制御を体験できる。

Usage:
    uv run streamlit run examples/app.py
"""

import streamlit as st
from common import setup_sidebar

setup_sidebar()

pg = st.navigation(
    [
        st.Page("pages/Home.py", title="Home", default=True),
        st.Page("pages/User.py", title="User"),
        st.Page("pages/Manager.py", title="Manager"),
        st.Page("pages/Admin.py", title="Admin"),
    ]
)
pg.run()
