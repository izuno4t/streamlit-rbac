"""streamlit-rbac デモアプリケーション.

サイドバーでユーザーとロールを切り替え、
ページ単位・コンポーネント単位のアクセス制御を体験できる。

Usage:
    uv run streamlit run example/app.py
"""

import streamlit as st
from common import Role, get_user_roles, setup_sidebar

from streamlit_rbac import has_role

setup_sidebar()

pages = [
    st.Page("pages/Home.py", title="Home", default=True),
    st.Page("pages/User.py", title="User"),
    st.Page("pages/Manager.py", title="Manager"),
]

if has_role(Role.ADMIN.value, role_loader=get_user_roles):
    pages.append(st.Page("pages/Admin.py", title="Admin"))

pg = st.navigation(pages)
pg.run()
