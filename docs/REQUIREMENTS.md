# streamlit-rbac

Streamlit向け軽量RBACライブラリ 要件定義書

| 項目 | 内容 |
| ------ | ------ |
| バージョン | 0.1.0（Draft） |
| 作成日 | 2026年1月24日 |
| ステータス | 検討中 |

---

## 目次

- [1. 概要](#1-概要)
  - [1.1 背景](#11-背景)
  - [1.2 目的](#12-目的)
  - [1.3 スコープ](#13-スコープ)
- [2. 設計方針](#2-設計方針)
  - [2.1 Spring Securityとの対比](#21-spring-securityとの対比)
  - [2.2 アーキテクチャ](#22-アーキテクチャ)
- [3. 機能要件](#3-機能要件)
  - [3.1 コア判定関数](#31-コア判定関数)
  - [3.2 デコレータ](#32-デコレータ)
  - [3.3 Streamlit統合](#33-streamlit統合)
- [4. インターフェース仕様](#4-インターフェース仕様)
  - [4.1 コア判定関数](#41-コア判定関数)
  - [4.2 デコレータ](#42-デコレータ)
  - [4.3 Streamlit統合](#43-streamlit統合)
- [5. 使用例](#5-使用例)
- [6. 非機能要件](#6-非機能要件)
- [7. 今後の拡張案（スコープ外）](#7-今後の拡張案スコープ外)

---

## 1. 概要

本ドキュメントは、Streamlitアプリケーション向けの軽量なRole-Based Access Control（RBAC）ライブラリ「streamlit-rbac」の要件を定義する。

### 1.1 背景

Streamlitはデータ分析やAIアプリケーションの迅速な開発に適したWebアプリケーションフレームワークであるが、認可機能が組み込まれていない。既存のPython RBACライブラリはFlaskやDjangoなど特定のフレームワークに依存するか、Casbinのように設定ファイルベースで複雑な構成を必要とする。

本ライブラリは、Spring SecurityのようなシンプルなAPIを提供し、開発者がロール取得ロジックを自由に実装できる薄いレイヤーを目指す。

### 1.2 目的

- Streamlitアプリケーションに宣言的なアクセス制御を提供する
- ロール取得ロジックを開発者が自由に実装できる拡張性を確保する
- Microsoft Entra ID等のIdPとの連携を容易にする
- ユニットテストが容易なAPIを提供する

### 1.3 スコープ

**対象範囲:**

- ロールベースのアクセス制御判定
- ページ単位・コンポーネント単位のアクセス制御
- Streamlitの`st.session_state`との統合

**対象外:**

- 認証機能（OAuth、OIDC等）
- ユーザー管理・ロール管理のUI
- データベーススキーマの提供

---

## 2. 設計方針

### 2.1 Spring Securityとの対比

本ライブラリはSpring Securityの認可機能を参考に、PythonらしいシンプルなAPIを提供する。

| Spring Security | streamlit-rbac |
| ----------------- | ---------------- |
| `hasRole("ADMIN")` | `has_role("Admin", ...)` |
| `hasAnyRole("A", "B")` | `has_any_role("A", "B", ...)` |
| `@PreAuthorize(...)` | `@require_roles(...)` |
| `SecurityFilterChain` | `guard_page(...)` |
| `UserDetails.getAuthorities()` | `role_loader`関数 |

### 2.2 アーキテクチャ

本ライブラリは3つのレイヤーで構成される。

| レイヤー | 責務 |
| --------- | ------ |
| コア判定関数 | `has_role()`, `has_any_role()`, `has_all_roles()` - 状態を持たない純粋関数 |
| デコレータ | `@require_roles()` - 関数・メソッドへの宣言的アクセス制御 |
| Streamlit統合 | `guard_page()`, ロールローダー - `st.session_state`との連携 |

---

## 3. 機能要件

### 3.1 コア判定関数

#### REQ-1: ロール直接指定による判定

必要なロール識別子とユーザーが持つロールの一覧を引数として受け取り、アクセス可否を真偽値で返却する。

```python
has_role("Admin", user_roles=["Admin", "User"])  # → True
```

#### REQ-2: ロールローダー関数による判定

必要なロール識別子と、ユーザーが持つロールを返却する関数を引数として受け取り、アクセス可否を真偽値で返却する。

```python
has_role("Admin", role_loader=lambda: current_user.roles)  # → True
```

#### REQ-3: 複数ロールの判定（OR条件）

指定されたロールのいずれかを持っているかを判定する。

```python
has_any_role("Admin", "Manager", user_roles=["Manager"])  # → True
```

#### REQ-4: 複数ロールの判定（AND条件）

指定されたロールのすべてを持っているかを判定する。

```python
has_all_roles("Admin", "Auditor", user_roles=["Admin", "Auditor"])  # → True
```

#### REQ-5: 排他的パラメータ検証

`user_roles`と`role_loader`の両方が指定された場合、またはどちらも指定されない場合は`ValueError`を発生させる。

### 3.2 デコレータ

#### REQ-6: 関数へのアクセス制御

`@require_roles`デコレータにより、関数実行前にロールチェックを行う。権限がない場合は`PermissionError`を発生させる。

```python
@require_roles("Admin", role_loader=get_user_roles)
def admin_function():
    ...
```

#### REQ-7: カスタム拒否ハンドラ

`on_denied`パラメータにより、権限拒否時のカスタム処理を指定できる。

### 3.3 Streamlit統合

#### REQ-8: ページガード関数

`guard_page()`関数により、ページ先頭でアクセス制御を行う。権限がない場合は`st.error()`でメッセージを表示し、`st.stop()`で処理を停止する。

```python
guard_page("Admin", role_loader=get_user_roles)
```

#### REQ-9: セッションベースのロールローダー

`st.session_state`からロールを取得する組み込みローダーを提供する。

```python
session_role_loader(session_key="user_roles")
```

#### REQ-10: ユーザーオブジェクトベースのロールローダー

`st.session_state`に格納されたユーザーオブジェクトの属性からロールを取得する組み込みローダーを提供する。

---

## 4. インターフェース仕様

### 4.1 コア判定関数

#### has_role()

| パラメータ | 型 | 説明 |
| ----------- | ----- | ------ |
| `required` | `str` | 必要なロール識別子 |
| `user_roles` | `Iterable[str] \| None` | ユーザーが持つロールの一覧（直接指定） |
| `role_loader` | `Callable[[], Iterable[str]] \| None` | ロールを返す関数（遅延評価） |

**戻り値:** `bool` - 指定ロールを持っている場合`True`

#### has_any_role()

| パラメータ | 型 | 説明 |
| ----------- | ----- | ------ |
| `*required` | `str` | 必要なロール識別子（可変長） |
| `user_roles` | `Iterable[str] \| None` | ユーザーが持つロールの一覧 |
| `role_loader` | `Callable[[], Iterable[str]] \| None` | ロールを返す関数 |

**戻り値:** `bool` - いずれかのロールを持っている場合`True`

#### has_all_roles()

| パラメータ | 型 | 説明 |
| ----------- | ----- | ------ |
| `*required` | `str` | 必要なロール識別子（可変長） |
| `user_roles` | `Iterable[str] \| None` | ユーザーが持つロールの一覧 |
| `role_loader` | `Callable[[], Iterable[str]] \| None` | ロールを返す関数 |

**戻り値:** `bool` - すべてのロールを持っている場合`True`

### 4.2 デコレータ

#### @require_roles()

| パラメータ | 型 | 説明 |
| ----------- | ----- | ------ |
| `*allowed_roles` | `str` | 許可するロール識別子（可変長） |
| `user_roles` | `Iterable[str] \| None` | ユーザーが持つロールの一覧 |
| `role_loader` | `Callable[[], Iterable[str]] \| None` | ロールを返す関数 |
| `on_denied` | `Callable[[], None] \| None` | 権限拒否時のコールバック |

**例外:** `PermissionError` - 権限がない場合

### 4.3 Streamlit統合

#### guard_page()

| パラメータ | 型 | 説明 |
| ----------- | ----- | ------ |
| `*allowed_roles` | `str` | 許可するロール識別子（可変長） |
| `role_loader` | `Callable[[], Iterable[str]]` | ロールを返す関数（必須） |
| `login_url` | `str \| None` | 未ログイン時のリダイレクト先 |

**動作:** 権限がない場合、`st.error()`表示後に`st.stop()`で処理停止

#### session_role_loader()

| パラメータ | 型 | 説明 |
| ----------- | ----- | ------ |
| `session_key` | `str` | `st.session_state`のキー（デフォルト: `"user_roles"`） |

**戻り値:** `Callable[[], Iterable[str]]` - ロールローダー関数

#### user_attr_role_loader()

| パラメータ | 型 | 説明 |
| ----------- | ----- | ------ |
| `user_session_key` | `str` | ユーザーオブジェクトのキー（デフォルト: `"user"`） |
| `role_attr` | `str` | ロール属性名（デフォルト: `"roles"`） |

**戻り値:** `Callable[[], Iterable[str]]` - ロールローダー関数

---

## 5. 使用例

### 5.1 基本的な使用例（ユニットテスト）

```python
# パターン1: ロールを直接渡す（テスト向き）
assert has_role("Admin", user_roles=["Admin", "User"]) == True
assert has_role("Admin", user_roles=["User"]) == False
assert has_any_role("Admin", "Manager", user_roles=["Manager"]) == True
```

### 5.2 Streamlitでの実運用

```python
# app.py - ロールローダーの定義
def get_user_roles() -> list[str]:
    user = st.session_state.get("user")
    if user is None:
        return []
    return user.roles

# pages/admin.py - ページガード
guard_page("Admin", role_loader=get_user_roles)
st.title("管理者ページ")

# コンポーネント単位の制御
if has_role("Admin", role_loader=get_user_roles):
    if st.button("ユーザー削除"):
        delete_user()
```

### 5.3 Microsoft Entra IDとの連携

```python
# Entra IDのトークンからロールを取得
def entra_role_loader() -> list[str]:
    token_claims = st.session_state.get("token_claims", {})
    return token_claims.get("roles", [])

# 使用
guard_page("Admin", role_loader=entra_role_loader)
```

---

## 6. 非機能要件

| 項目 | 要件 |
| ------ | ------ |
| Python バージョン | 3.10以上 |
| 依存関係 | コア機能は標準ライブラリのみ。Streamlit統合は`streamlit`をオプショナル依存とする |
| テストカバレッジ | 90%以上 |
| 型ヒント | すべての公開APIに型ヒントを付与 |
| ドキュメント | docstringによるAPI仕様の記述、READMEによる使用例の提供 |

---

## 7. 今後の拡張案（スコープ外）

- パーミッションベースのアクセス制御（RBAC + Permission）
- ロール階層（Admin > Manager > User）
- 監査ログ機能
- FastAPI / Flask 向けの統合モジュール
