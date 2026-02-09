# streamlit-rbac

Streamlit向け軽量RBACライブラリ アプリケーション仕様書

| 項目 | 内容 |
| ------ | ------ |
| バージョン | 0.1.0（Draft） |
| 作成日 | 2026年2月9日 |
| 対応要件定義書 | streamlit-rbac 要件定義書 v0.1.0 |
| ステータス | 検討中 |

---

## 目次

- [1. 概要](#1-概要)
  - [1.1 ライブラリの位置づけ](#11-ライブラリの位置づけ)
  - [1.2 レイヤー概要](#12-レイヤー概要)
- [2. 型定義](#2-型定義)
  - [2.1 RoleLoader](#21-roleloader)
  - [2.2 OnDeniedHandler](#22-ondeniedhandler)
  - [2.3 ロール識別子の仕様](#23-ロール識別子の仕様)
- [3. コア判定関数](#3-コア判定関数)
  - [3.1 ロール解決の共通ルール](#31-ロール解決の共通ルール)
  - [3.2 has_role()](#32-has_role)
  - [3.3 has_any_role()](#33-has_any_role)
  - [3.4 has_all_roles()](#34-has_all_roles)
- [4. デコレータ](#4-デコレータ)
  - [4.1 @require_roles()](#41-require_roles)
- [5. Streamlit統合](#5-streamlit統合)
  - [5.1 authorize_page()](#51-authorize_page)
- [6. エラー仕様](#6-エラー仕様)
- [7. 統合シナリオ](#7-統合シナリオ)
  - [7.1 マルチページアプリケーション構成例](#71-マルチページアプリケーション構成例)
- [8. 非機能仕様](#8-非機能仕様)
- [9. 要件トレーサビリティ](#9-要件トレーサビリティ)

---

## 1. 概要

本ドキュメントは、streamlit-rbac の外部仕様を定義する。各APIの振る舞い、入出力、エラー条件、および利用シナリオを記述する。内部実装の詳細は設計書を参照のこと。

### 1.1 ライブラリの位置づけ

streamlit-rbac は「ロールベースのアクセス制御判定」のみを責務とする薄いレイヤーである。認証（OAuth、OIDC等）、ユーザー管理、セッション管理はスコープ外とし、利用側のアプリケーションに委ねる。

ロール取得ロジックを `role_loader` 関数として外部から注入させることで、IdP連携やカスタム認証基盤との統合を開発者が完全に制御できる。ライブラリは判定ロジックのみを提供し、ロールの出所には関与しない。

### 1.2 レイヤー概要

本ライブラリは3つのレイヤーで構成される。各レイヤーは上位から下位への一方向依存とする。

| レイヤー | 責務 | streamlit依存 |
| --------- | ------ | -------------- |
| コア判定関数 | 状態を持たない純粋関数によるロール判定 | なし |
| デコレータ | 関数への宣言的アクセス制御 | なし |
| Streamlit統合 | `st.session_state` との連携、ページガード | あり |

---

## 2. 型定義

### 2.1 RoleLoader

```python
RoleLoader = Callable[[], Iterable[str]]
```

ユーザーのロール一覧を返す関数の型。IdPやセッションからロールを取得するロジックを表現する。呼び出し時にロールを解決する遅延評価を前提とする。

### 2.2 OnDeniedHandler

```python
OnDeniedHandler = Callable[[], None]
```

権限拒否時に実行されるコールバック関数の型。デコレータで権限が不足した場合に呼び出される。

### 2.3 ロール識別子の仕様

ロール識別子は `str` 型とする。比較は大文字・小文字を区別する（case-sensitive）。これはIdPから返却されるロール文字列をそのまま使用することを前提とするためである。利用側で `Enum` を定義し `.value` で渡す運用は妨げない。

---

## 3. コア判定関数

### 3.1 ロール解決の共通ルール

コア判定関数（`has_role`, `has_any_role`, `has_all_roles`）はすべて、ユーザーのロールを取得するために `user_roles` または `role_loader` のいずれか一方を受け取る。

**排他制約（REQ-5）:**

| `user_roles` | `role_loader` | 結果 |
| :---: | :---: | :--- |
| 指定あり | `None` | `user_roles` を使用 |
| `None` | 指定あり | `role_loader()` を呼び出して使用 |
| 指定あり | 指定あり | `ValueError` |
| `None` | `None` | `ValueError` |

### 3.2 has_role()

**対応要件:** REQ-1, REQ-2

指定された単一のロールを保持しているかを判定する。

```python
has_role(
    required: str,
    *,
    user_roles: Iterable[str] | None = None,
    role_loader: RoleLoader | None = None,
) -> bool
```

**振る舞い:**

| 条件 | 戻り値 |
| ------ | -------- |
| `required` が解決されたロール集合に含まれる | `True` |
| `required` が解決されたロール集合に含まれない | `False` |

**使用例:**

```python
has_role("Admin", user_roles=["Admin", "User"])      # → True
has_role("Admin", user_roles=["User"])                # → False
has_role("Admin", user_roles=["admin"])               # → False（case-sensitive）
has_role("Admin", role_loader=lambda: ["Admin"])       # → True
```

### 3.3 has_any_role()

**対応要件:** REQ-3

指定されたロールのいずれかを保持しているかを判定する。

```python
has_any_role(
    *required: str,
    user_roles: Iterable[str] | None = None,
    role_loader: RoleLoader | None = None,
) -> bool
```

**振る舞い:**

| 条件 | 戻り値 |
| ------ | -------- |
| `required` のいずれかが解決されたロール集合に含まれる | `True` |
| `required` のいずれも含まれない | `False` |
| `required` が空（引数なし） | `False` |

`required` が空の場合に `False` を返すのは、「いずれかのロールを持っている」という命題が判定対象の不在により偽となるためである。

**使用例:**

```python
has_any_role("Admin", "Manager", user_roles=["Manager"])  # → True
has_any_role("Admin", "Manager", user_roles=["User"])     # → False
has_any_role(user_roles=["Admin"])                         # → False（required空）
```

### 3.4 has_all_roles()

**対応要件:** REQ-4

指定されたロールのすべてを保持しているかを判定する。

```python
has_all_roles(
    *required: str,
    user_roles: Iterable[str] | None = None,
    role_loader: RoleLoader | None = None,
) -> bool
```

**振る舞い:**

| 条件 | 戻り値 |
| ------ | -------- |
| `required` のすべてが解決されたロール集合に含まれる | `True` |
| `required` のいずれかが含まれない | `False` |
| `required` が空（引数なし） | `True` |

`required` が空の場合に `True` を返すのは、空集合は任意の集合の部分集合であるため（vacuous truth）。これは `all([])` が `True` を返すPythonの慣例とも一致する。

**使用例:**

```python
has_all_roles("Admin", "Auditor", user_roles=["Admin", "Auditor"])       # → True
has_all_roles("Admin", "Auditor", user_roles=["Admin"])                  # → False
has_all_roles("Admin", "Auditor", user_roles=["Admin", "Auditor", "X"]) # → True
has_all_roles(user_roles=["Admin"])                                      # → True（required空）
```

---

## 4. デコレータ

### 4.1 @require_roles()

**対応要件:** REQ-6, REQ-7

関数実行前にロールチェックを行うデコレータ。指定されたロールのいずれかを持っていない場合、関数を実行せずにエラーとする。内部的に `has_any_role` を使用する（OR条件）。

```python
@require_roles(
    *allowed_roles: str,
    user_roles: Iterable[str] | None = None,
    role_loader: RoleLoader | None = None,
    on_denied: OnDeniedHandler | None = None,
)
```

**振る舞い:**

| 条件 | 動作 |
| ------ | ------ |
| ロール判定が `True` | 元の関数を実行し、その戻り値を返す |
| ロール判定が `False`、`on_denied` なし | `PermissionError` を送出 |
| ロール判定が `False`、`on_denied` あり | `on_denied()` を呼び出した後、`PermissionError` を送出 |

`on_denied` はログ記録やUIフィードバックのための副作用処理であり、元の関数の実行を許可するゲートではない。
`on_denied` 内で独自の例外を送出すれば、その例外が `PermissionError` より先に伝搬する。
`on_denied` が正常にreturnした場合も、元の関数は実行されない。

デコレートされた関数は `functools.wraps` により、元の関数の `__name__`、`__doc__` 等のメタデータを保持する。

**使用例:**

```python
@require_roles("Admin", role_loader=get_user_roles)
def delete_user(user_id: str) -> None:
    ...

@require_roles("Admin", "Manager", user_roles=["User"], on_denied=log_violation)
def sensitive_action() -> None:
    ...
```

---

## 5. Streamlit統合

### 5.1 authorize_page()

**対応要件:** REQ-8

ページスクリプトの先頭で呼び出し、アクセス制御を行う関数。権限がない場合はStreamlitのUIにメッセージを表示し、後続の処理を停止する。

```python
authorize_page(
    *allowed_roles: str,
    role_loader: RoleLoader,
    login_url: str | None = None,
    denied_message: str = "このページへのアクセス権限がありません。",
) -> None
```

**振る舞い:**

```text
role_loader() を呼び出し
  │
  ├─ ロール一覧が空（未ログインと推定）
  │    ├─ login_url 指定あり → st.warning + ログインリンク表示 + st.stop()
  │    └─ login_url 指定なし → st.error("ログインが必要です。") + st.stop()
  │
  ├─ ロール判定 True（いずれかのロールを保持）
  │    └─ 正常終了（後続のページコードが実行される）
  │
  └─ ロール判定 False
       └─ st.error(denied_message) + st.stop()
```

`authorize_page` は例外を送出しない。`st.stop()` によりStreamlitのスクリプト実行が停止し、この関数以降のコードは実行されない。

**使用例:**

```python
# pages/admin.py
authorize_page("Admin", role_loader=get_user_roles)
st.title("管理者ページ")  # 権限がない場合、ここには到達しない

# ログインURLを指定する場合
authorize_page("Admin", role_loader=get_user_roles, login_url="/login")
```

---

## 6. エラー仕様

本ライブラリは独自の例外クラスを定義せず、Pythonの組み込み例外を使用する。

| 例外 | 発生箇所 | 発生条件 | メッセージ |
| ------ | --------- | --------- | ----------- |
| `ValueError` | コア判定関数 | `user_roles` と `role_loader` の両方が指定された | `"user_roles and role_loader are mutually exclusive..."` |
| `ValueError` | コア判定関数 | `user_roles` と `role_loader` のどちらも指定されない | `"Either user_roles or role_loader must be specified."` |
| `PermissionError` | `@require_roles` | ロール判定で権限不足と判定された | `"Access denied: required one of (...)"` |

`authorize_page` は例外を送出せず、`st.error()` + `st.stop()` でページ描画を停止する。

---

## 7. 統合シナリオ

### 7.1 マルチページアプリケーション構成例

```python
# app.py - アプリケーション共通のロールローダー
def get_user_roles() -> list[str]:
    claims = st.session_state.get("token_claims", {})
    return claims.get("roles", [])

# pages/dashboard.py - 複数ロール許可
authorize_page("User", "Admin", role_loader=get_user_roles)
st.title("ダッシュボード")

# pages/admin.py - ページガード + コンポーネント単位の制御
authorize_page("Admin", role_loader=get_user_roles)
st.title("管理者ページ")

if has_role("SuperAdmin", role_loader=get_user_roles):
    with st.expander("システム設定"):
        st.write("危険な操作...")
```

---

## 8. 非機能仕様

| 項目 | 仕様 |
| ------ | ------ |
| Python バージョン | 3.11以上 |
| 依存関係 | コア機能は標準ライブラリのみ。Streamlit統合は `streamlit>=1.24.0` をオプショナル依存 |
| テストカバレッジ | 90%以上 |
| 型ヒント | すべての公開APIに型ヒントを付与。`mypy --strict` を通過すること |
| ドキュメント | すべての公開APIにdocstringを付与 |
| エラーメッセージ | ライブラリのエラーメッセージは英語。UIメッセージは利用側で制御可能 |

---

## 9. 要件トレーサビリティ

| 要件ID | 要件名 | 対応API |
| -------- | -------- | --------- |
| REQ-1 | ロール直接指定による判定 | `has_role(user_roles=...)` |
| REQ-2 | ロールローダー関数による判定 | `has_role(role_loader=...)` |
| REQ-3 | 複数ロールの判定（OR条件） | `has_any_role()` |
| REQ-4 | 複数ロールの判定（AND条件） | `has_all_roles()` |
| REQ-5 | 排他的パラメータ検証 | コア判定関数共通 |
| REQ-6 | 関数へのアクセス制御 | `@require_roles()` |
| REQ-7 | カスタム拒否ハンドラ | `@require_roles(on_denied=...)` |
| REQ-8 | ページガード関数 | `authorize_page()` |
