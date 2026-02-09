# streamlit-rbac サンプルアプリケーション

`streamlit-rbac` を使ったロールベースのアクセス制御を、Streamlit のマルチページアプリケーションで体験できるデモです。

## 起動方法

プロジェクトルートで以下を実行してください。

```bash
uv run streamlit run example/app.py
```

ブラウザが開きます。サイドバーでユーザーを切り替えると、各ページのアクセス制御の動作を確認できます。

## ファイル構成

```text
example/
  app.py            エントリポイント。ロールに応じてナビゲーションを動的に構築
  common.py         共有モジュール: ロール定義、ユーザー定義、ロールローダー
  pages/
    Home.py         公開ページ（認可不要）
    User.py         User / Manager / Admin がアクセス可能
    Manager.py      Manager / Admin がアクセス可能
    Admin.py        Admin のみアクセス可能
```

## 導入手順

### 1. ロールローダーを定義する

`streamlit-rbac` はロールの取得方法を規定しません。
`RoleLoader`（`Callable[[], Iterable[str]]`）に合致する関数を実装し、`role_loader` 引数に渡します。

```python
# common.py
def get_user_roles() -> list[str]:
    return st.session_state.get("user_roles", [])
```

取得元はセッション、データベース、IdP トークンなど自由です。

### 2. ロールに応じてナビゲーションリンクを出し分ける

`st.navigation` に渡すページリストを動的に組み立て、権限のないユーザーにはリンク自体を表示しないようにします。

```python
# app.py
from streamlit_rbac import has_role

pages = [
    st.Page("pages/Home.py", title="Home", default=True),
    st.Page("pages/User.py", title="User"),
    st.Page("pages/Manager.py", title="Manager"),
]

if has_role("Admin", role_loader=get_user_roles):
    pages.append(st.Page("pages/Admin.py", title="Admin"))

pg = st.navigation(pages)
pg.run()
```

サイドバーにはアクセス可能なページだけが表示されます。

### 3. `authorize_page()` でページを保護する

ナビゲーションリンクを非表示にしても、URL を直接入力すればページにアクセスできます。
各ページスクリプトの先頭で `authorize_page()` を呼び出し、フォールバックとして保護します。

```python
# pages/Admin.py
from streamlit_rbac import authorize_page

authorize_page("Admin", role_loader=get_user_roles)

st.header("Admin ページ")  # 権限がなければここには到達しない
```

手順 2 と手順 3 を組み合わせることで多層防御になります。ナビゲーションでリンクを隠し、`authorize_page()` で直接アクセスをブロックします。

### 4. `has_role()` / `has_any_role()` でコンポーネント単位の制御を行う

ページ内の一部セクションだけ特定ロールに限定したい場合は、コア関数で条件分岐します。

```python
# pages/User.py
from streamlit_rbac import has_any_role

if has_any_role("Manager", "Admin", role_loader=get_user_roles):
    st.subheader("詳細レポート（Manager / Admin のみ）")
```

### 5. ロール識別子に Enum を使う

文字列リテラルの散在を防ぐため、`Role` enum を定義して `.value` で渡す運用を推奨します。

```python
from enum import Enum

class Role(Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    USER = "User"

authorize_page(Role.ADMIN.value, role_loader=get_user_roles)
```

## デモユーザー

| ユーザー | ロール |
| --- | --- |
| alice (Admin) | Admin, User |
| bob (Manager) | Manager, User |
| charlie (User) | User |
| guest | (なし) |

サイドバーでユーザーを切り替えると、ナビゲーションリンク・ページアクセス・コンポーネントの表示がロールに応じて変化します。
