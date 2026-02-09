# streamlit-rbac

Streamlit向け軽量RBACライブラリ 設計書

| 項目 | 内容 |
| ------ | ------ |
| バージョン | 0.1.0（Draft） |
| 作成日 | 2026年2月9日 |
| 対応仕様書 | streamlit-rbac アプリケーション仕様書 v0.1.0 |
| ステータス | 検討中 |

---

## 目次

- [1. 設計方針](#1-設計方針)
  - [1.1 基本原則](#11-基本原則)
  - [1.2 レイヤー依存関係](#12-レイヤー依存関係)
- [2. プロジェクト構成](#2-プロジェクト構成)
  - [2.1 ディレクトリ構造](#21-ディレクトリ構造)
  - [2.2 モジュール命名規約](#22-モジュール命名規約)
  - [2.3 pyproject.toml](#23-pyprojecttoml)
- [3. モジュール詳細設計](#3-モジュール詳細設計)
  - [3.1 _types.py](#31-_typespy)
  - [3.2 _core.py](#32-_corepy)
  - [3.3 _decorators.py](#33-_decoratorspy)
  - [3.4 _streamlit.py](#34-_streamlitpy)
  - [3.5 \_\_init\_\_.py](#35-__init__py)
- [4. 独自例外を定義しない理由](#4-独自例外を定義しない理由)
- [5. テスト戦略](#5-テスト戦略)
  - [5.1 テスト分類](#51-テスト分類)
  - [5.2 test_core.py](#52-test_corepy)
  - [5.3 test_decorators.py](#53-test_decoratorspy)
  - [5.4 test_streamlit.py](#54-test_streamlitpy)
- [6. 要件トレーサビリティ（実装・テスト対応）](#6-要件トレーサビリティ実装テスト対応)
- [7. 今後の検討事項](#7-今後の検討事項)

---

## 1. 設計方針

### 1.1 基本原則

**純粋関数を中核に据える設計:** コア判定関数は副作用を持たない純粋関数として実装する。これにより、ユニットテストが容易になり、Streamlit以外の文脈でも利用可能となる。上位レイヤー（デコレータ、Streamlit統合）は、このコア関数を合成・ラップする形で構築する。

**Spring Securityとの対比を意識したAPI設計:** 要件定義書で示された対応関係に基づき、Javaエンジニアにとっても直感的なAPIを提供する。ただし、Pythonの慣例（snake_case、keyword-only引数、デコレータ構文）に従う。

### 1.2 レイヤー依存関係

```text
┌─────────────────────────────────────┐
│   Streamlit統合レイヤー              │  authorize_page()
│   Streamlitのセッション・UIと連携    │
├─────────────────────────────────────┤
│   デコレータレイヤー                 │  @require_roles()
│   関数への宣言的アクセス制御         │
├─────────────────────────────────────┤
│   コア判定レイヤー                   │  has_role(), has_any_role()
│   状態を持たない純粋関数             │  has_all_roles()
└─────────────────────────────────────┘
```

依存方向は上から下への一方向。コア判定レイヤーは他のレイヤーおよび外部パッケージに一切依存しない。Streamlit統合レイヤーのみが `streamlit` パッケージに依存する。

---

## 2. プロジェクト構成

### 2.1 ディレクトリ構造

```text
streamlit-rbac/
├── src/
│   └── streamlit_rbac/
│       ├── __init__.py          # 公開API再エクスポート
│       ├── _core.py             # コア判定関数
│       ├── _decorators.py       # デコレータ
│       ├── _streamlit.py        # Streamlit統合
│       ├── _types.py            # 型定義
│       └── _exceptions.py       # カスタム例外（将来の拡張ポイント）
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_decorators.py
│   └── test_streamlit.py
├── pyproject.toml
├── README.md
└── LICENSE
```

### 2.2 モジュール命名規約

内部モジュールは先頭にアンダースコアを付与し（`_core.py` 等）、直接importされることを意図しないことを示す。
すべての公開APIは `__init__.py` で再エクスポートし、
利用者は常に `from streamlit_rbac import has_role` の形でimportする。

### 2.3 pyproject.toml

```toml
[project]
name = "streamlit-rbac"
version = "0.1.0"
description = "Lightweight RBAC library for Streamlit applications"
requires-python = ">=3.10"
license = "MIT"
dependencies = []

[project.optional-dependencies]
streamlit = ["streamlit>=1.24.0"]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.4",
    "mypy>=1.10",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/streamlit_rbac"]

[tool.ruff]
target-version = "py310"
src = ["src"]

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "A", "SIM", "TCH"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.mypy]
python_version = "3.10"
strict = true

[tool.coverage.run]
source = ["streamlit_rbac"]

[tool.coverage.report]
fail_under = 90
```

---

## 3. モジュール詳細設計

### 3.1 _types.py

```python
"""streamlit-rbac の型定義."""

from collections.abc import Callable, Iterable
from typing import TypeAlias

RoleLoader: TypeAlias = Callable[[], Iterable[str]]
"""ユーザーのロール一覧を返す関数の型."""

OnDeniedHandler: TypeAlias = Callable[[], None]
"""権限拒否時に実行されるコールバック関数の型."""
```

### 3.2 _core.py

```python
"""streamlit-rbac のコア判定関数.

状態を持たない純粋関数としてロールベースのアクセス判定を提供する。
すべての関数は標準ライブラリのみに依存する。
"""

from __future__ import annotations

from collections.abc import Iterable

from streamlit_rbac._types import RoleLoader


def _resolve_roles(
    user_roles: Iterable[str] | None,
    role_loader: RoleLoader | None,
) -> frozenset[str]:
    """ユーザーロールを解決する内部関数.

    user_roles と role_loader の排他チェックを行い、
    ロール一覧を frozenset として返却する。

    Raises:
        ValueError: 両方が指定された場合、またはどちらも指定されない場合.
    """
    if user_roles is not None and role_loader is not None:
        msg = (
            "user_roles and role_loader are mutually exclusive. "
            "Specify one or the other, not both."
        )
        raise ValueError(msg)
    if user_roles is None and role_loader is None:
        msg = "Either user_roles or role_loader must be specified."
        raise ValueError(msg)

    if user_roles is not None:
        return frozenset(user_roles)

    assert role_loader is not None
    return frozenset(role_loader())


def has_role(
    required: str,
    *,
    user_roles: Iterable[str] | None = None,
    role_loader: RoleLoader | None = None,
) -> bool:
    """指定されたロールを保持しているかを判定する."""
    resolved = _resolve_roles(user_roles, role_loader)
    return required in resolved


def has_any_role(
    *required: str,
    user_roles: Iterable[str] | None = None,
    role_loader: RoleLoader | None = None,
) -> bool:
    """指定されたロールのいずれかを保持しているかを判定する."""
    if not required:
        return False
    resolved = _resolve_roles(user_roles, role_loader)
    return bool(resolved & frozenset(required))


def has_all_roles(
    *required: str,
    user_roles: Iterable[str] | None = None,
    role_loader: RoleLoader | None = None,
) -> bool:
    """指定されたロールのすべてを保持しているかを判定する."""
    if not required:
        return True
    resolved = _resolve_roles(user_roles, role_loader)
    return frozenset(required) <= resolved
```

#### 設計判断: コア判定

**`_resolve_roles` の戻り値に `frozenset` を採用した理由:** ロール判定は集合演算（`in`, `&`, `<=`）で効率的に表現できる。`frozenset` は不変であり、コア関数が副作用を持たないことを型レベルで保証する。

**排他チェックを共通関数に切り出した理由:** 3つのコア判定関数すべてで同一のバリデーションロジックが必要であり、DRYの原則に従う。また、この関数をテスト対象とすることで排他チェックのテストを一箇所に集約できる。

**エラーメッセージを英語とした理由:** ライブラリのエラーメッセージは開発者が読むものであり、国際的な利用を想定して英語とした。

### 3.3 _decorators.py

```python
"""streamlit-rbac のデコレータ."""

from __future__ import annotations

import functools
from collections.abc import Callable, Iterable
from typing import ParamSpec, TypeVar

from streamlit_rbac._core import has_any_role
from streamlit_rbac._types import OnDeniedHandler, RoleLoader

P = ParamSpec("P")
R = TypeVar("R")


def require_roles(
    *allowed_roles: str,
    user_roles: Iterable[str] | None = None,
    role_loader: RoleLoader | None = None,
    on_denied: OnDeniedHandler | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """関数実行前にロールチェックを行うデコレータ."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if not has_any_role(
                *allowed_roles,
                user_roles=user_roles,
                role_loader=role_loader,
            ):
                if on_denied is not None:
                    on_denied()
                msg = f"Access denied: required one of {allowed_roles}"
                raise PermissionError(msg)
            return func(*args, **kwargs)

        return wrapper

    return decorator
```

#### 設計判断: デコレータ

**OR条件をデフォルトとした理由:**
Spring Securityの `hasAnyRole` と同様に、「許可されたロールのいずれかを持っていればアクセス可」というのが最も一般的なユースケースである。
AND条件が必要な場合はデコレータを重ねるか、`has_all_roles` をガード関数内で直接使用する。

**`on_denied` 呼び出し後も `PermissionError` を送出する理由:**
`on_denied` はログ記録やUIフィードバックのための副作用処理であり、元の関数の実行を許可するゲートではない。
`on_denied` 内で独自の例外を送出すれば、その例外が `PermissionError` より先に伝搬する。
`on_denied` が正常にreturnした場合でも、元の関数が実行されることは安全上望ましくない。

**`ParamSpec` / `TypeVar` による型保持:** デコレートされた関数の引数型・戻り値型を保持するために `ParamSpec` と `TypeVar` を使用する。これにより `mypy --strict` での型チェックが通る。

### 3.4 _streamlit.py

```python
"""streamlit-rbac の Streamlit統合.

st.session_state との連携およびページガード機能を提供する。
このモジュールは streamlit パッケージに依存する。
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from streamlit_rbac._core import has_any_role
from streamlit_rbac._types import RoleLoader


def authorize_page(
    *allowed_roles: str,
    role_loader: RoleLoader,
    login_url: str | None = None,
    denied_message: str = "このページへのアクセス権限がありません。",
) -> None:
    """ページ先頭でアクセス制御を行う."""
    import streamlit as st

    user_roles = list(role_loader())

    if not user_roles:
        if login_url is not None:
            st.warning("ログインが必要です。")
            st.link_button("ログインページへ", login_url)
            st.stop()
        st.error("ログインが必要です。")
        st.stop()

    if not has_any_role(*allowed_roles, user_roles=user_roles):
        st.error(denied_message)
        st.stop()
```

#### 設計判断: Streamlit統合

**`streamlit` の遅延importを採用した理由:** `import streamlit` を関数内で行うことで、コア機能・デコレータのみを使用する場合に `streamlit` がインストールされていなくてもimportエラーが発生しない。これによりオプショナル依存の意図を実現する。

**組み込みロールローダーを提供しない理由:**
ライブラリの設計方針は「ロール取得は開発者の責任」であり、
`st.session_state` の構造に依存するローダーをライブラリ側で提供することはスコープの拡大にあたる。
`RoleLoader` 型をインターフェースとして定義し、実装は開発者に委ねる。

**未ログイン判定の分離:** `authorize_page` は role_loader が空リストを返した場合を「未ログイン」と推定し、`login_url` が指定されている場合はログインページへのリンクを表示する。これは認可ライブラリの責務をやや逸脱するが、Streamlitにおける実用性を優先した。

### 3.5 \_\_init\_\_.py

```python
"""streamlit-rbac: Lightweight RBAC library for Streamlit applications."""

from streamlit_rbac._core import has_all_roles, has_any_role, has_role
from streamlit_rbac._decorators import require_roles
from streamlit_rbac._types import OnDeniedHandler, RoleLoader

__all__ = [
    "has_role",
    "has_any_role",
    "has_all_roles",
    "require_roles",
    "RoleLoader",
    "OnDeniedHandler",
]


def __getattr__(name: str):
    """Streamlit統合モジュールの遅延import."""
    if name == "authorize_page":
        from streamlit_rbac._streamlit import authorize_page
        return authorize_page
    raise AttributeError(f"module 'streamlit_rbac' has no attribute {name!r}")
```

#### 設計判断: `__getattr__` による遅延import

モジュールレベルの `__getattr__`（PEP 562）を使用し、Streamlit統合のシンボルを初回アクセス時にimportする。これにより以下を実現する。

- `from streamlit_rbac import authorize_page` は `streamlit` がインストールされていない環境でもimport自体はエラーにならない
- `authorize_page()` の呼び出し時に初めて `streamlit` のimportが試行される
- コア機能のみを使用するユーザーは `streamlit` を依存に含める必要がない
- Streamlit統合の公開APIは `authorize_page` のみであり、`__getattr__` のルックアップ対象もこの1つに限定している

---

## 4. 独自例外を定義しない理由

`AccessDeniedError` 等の独自例外を定義することも検討したが、以下の理由から見送った。

- 本ライブラリは薄いレイヤーであり、独自の例外階層を持つ必要がない
- `PermissionError` はPython組み込みの例外であり、意味的に正確である
- 利用者が `except PermissionError` でキャッチする際に、追加のimportが不要

`_exceptions.py` はファイルとして残し、v1.0で独自例外が必要になった場合の拡張ポイントとする。

---

## 5. テスト戦略

### 5.1 テスト分類

| レイヤー | テスト対象 | テスト手法 | streamlit依存 |
| --------- | ---------- | ---------- | -------------- |
| コア判定 | `has_role`, `has_any_role`, `has_all_roles` | パラメタライズドテスト | なし |
| コア判定 | `_resolve_roles` | 排他チェックの異常系テスト | なし |
| デコレータ | `require_roles` | デコレート済み関数の呼び出しテスト | なし |
| Streamlit統合 | `authorize_page` | `st.session_state` のモック | モック使用 |

### 5.2 test_core.py

```python
"""コア判定関数のテスト."""

import pytest

from streamlit_rbac import has_all_roles, has_any_role, has_role


class TestHasRole:

    @pytest.mark.parametrize(
        ("required", "user_roles", "expected"),
        [
            ("Admin", ["Admin", "User"], True),
            ("Admin", ["User"], False),
            ("Admin", [], False),
            ("Admin", ["admin"], False),  # case-sensitive
        ],
    )
    def test_with_user_roles(
        self, required: str, user_roles: list[str], expected: bool
    ) -> None:
        assert has_role(required, user_roles=user_roles) == expected

    def test_with_role_loader(self) -> None:
        loader = lambda: ["Admin", "User"]
        assert has_role("Admin", role_loader=loader) is True

    def test_mutual_exclusion_both_specified(self) -> None:
        with pytest.raises(ValueError, match="mutually exclusive"):
            has_role("Admin", user_roles=["Admin"], role_loader=lambda: [])

    def test_mutual_exclusion_neither_specified(self) -> None:
        with pytest.raises(ValueError, match="must be specified"):
            has_role("Admin")


class TestHasAnyRole:

    def test_match_one(self) -> None:
        assert has_any_role("Admin", "Manager", user_roles=["Manager"]) is True

    def test_no_match(self) -> None:
        assert has_any_role("Admin", "Manager", user_roles=["User"]) is False

    def test_empty_required(self) -> None:
        assert has_any_role(user_roles=["Admin"]) is False


class TestHasAllRoles:

    def test_all_present(self) -> None:
        assert (
            has_all_roles("Admin", "Auditor", user_roles=["Admin", "Auditor"]) is True
        )

    def test_partial(self) -> None:
        assert has_all_roles("Admin", "Auditor", user_roles=["Admin"]) is False

    def test_superset(self) -> None:
        assert (
            has_all_roles(
                "Admin", "Auditor", user_roles=["Admin", "Auditor", "User"]
            )
            is True
        )

    def test_empty_required(self) -> None:
        assert has_all_roles(user_roles=["Admin"]) is True
```

### 5.3 test_decorators.py

```python
"""デコレータのテスト."""

import pytest

from streamlit_rbac import require_roles


class TestRequireRoles:

    def test_allowed(self) -> None:
        @require_roles("Admin", user_roles=["Admin"])
        def action() -> str:
            return "ok"

        assert action() == "ok"

    def test_denied(self) -> None:
        @require_roles("Admin", user_roles=["User"])
        def action() -> str:
            return "ok"

        with pytest.raises(PermissionError):
            action()

    def test_on_denied_callback(self) -> None:
        callback_called = False

        def on_denied() -> None:
            nonlocal callback_called
            callback_called = True

        @require_roles("Admin", user_roles=["User"], on_denied=on_denied)
        def action() -> str:
            return "ok"

        with pytest.raises(PermissionError):
            action()
        assert callback_called is True

    def test_on_denied_custom_exception(self) -> None:
        """on_denied 内で送出された例外が PermissionError より優先される."""

        class CustomError(Exception):
            pass

        def on_denied() -> None:
            raise CustomError("custom")

        @require_roles("Admin", user_roles=["User"], on_denied=on_denied)
        def action() -> str:
            return "ok"

        with pytest.raises(CustomError, match="custom"):
            action()

    def test_preserves_function_metadata(self) -> None:
        @require_roles("Admin", user_roles=["Admin"])
        def my_function() -> None:
            """My docstring."""

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

    def test_with_arguments(self) -> None:
        @require_roles("Admin", user_roles=["Admin"])
        def greet(name: str) -> str:
            return f"Hello, {name}"

        assert greet("Alice") == "Hello, Alice"
```

### 5.4 test_streamlit.py

Streamlit統合のテストでは `unittest.mock.patch` を用いて `streamlit` モジュール自体をモック化し、テスト実行時にStreamlitの依存を不要とする。

```python
"""Streamlit統合のテスト."""

from unittest.mock import MagicMock, patch

import pytest


class TestAuthorizePage:

    def test_allowed(self) -> None:
        mock_st = MagicMock()

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import authorize_page

            authorize_page("Admin", role_loader=lambda: ["Admin"])
            mock_st.error.assert_not_called()
            mock_st.stop.assert_not_called()

    def test_denied(self) -> None:
        mock_st = MagicMock()

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import authorize_page

            authorize_page("Admin", role_loader=lambda: ["User"])
            mock_st.error.assert_called_once()
            mock_st.stop.assert_called_once()

    def test_unauthenticated_with_login_url(self) -> None:
        mock_st = MagicMock()

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import authorize_page

            authorize_page("Admin", role_loader=lambda: [], login_url="/login")
            mock_st.warning.assert_called_once()
            mock_st.link_button.assert_called_once_with(
                "ログインページへ", "/login"
            )
            mock_st.stop.assert_called_once()
```

---

## 6. 要件トレーサビリティ（実装・テスト対応）

| 要件ID | 要件名 | 実装モジュール | テストクラス |
| -------- | -------- | ------------- | ------------ |
| REQ-1 | ロール直接指定による判定 | `_core.has_role` | `TestHasRole.test_with_user_roles` |
| REQ-2 | ロールローダー関数による判定 | `_core.has_role` | `TestHasRole.test_with_role_loader` |
| REQ-3 | 複数ロールの判定（OR条件） | `_core.has_any_role` | `TestHasAnyRole` |
| REQ-4 | 複数ロールの判定（AND条件） | `_core.has_all_roles` | `TestHasAllRoles` |
| REQ-5 | 排他的パラメータ検証 | `_core._resolve_roles` | `TestHasRole.test_mutual_exclusion_*` |
| REQ-6 | 関数へのアクセス制御 | `_decorators.require_roles` | `TestRequireRoles.test_allowed/denied` |
| REQ-7 | カスタム拒否ハンドラ | `_decorators.require_roles` | `TestRequireRoles.test_on_denied_*` |
| REQ-8 | ページガード関数 | `_streamlit.authorize_page` | `TestAuthorizePage` |

---

## 7. 今後の検討事項

| 項目 | 内容 | 優先度 |
| ------ | ------ | -------- |
| `denied_message` のデフォルト言語 | 英語に変更するか、i18n対応するか | 中 |
| `authorize_page` の戻り値 | `None` ではなく `bool` を返して `st.stop()` を呼び出し側に委ねる案 | 低 |
| `py.typed` マーカーの同梱 | PEP 561準拠の型情報配布 | 高 |
| `_exceptions.py` の活用 | v1.0で独自例外が必要になった場合の拡張ポイントとして保持 | 低 |
| ロールの正規化オプション | case-insensitive比較のオプション提供 | 低 |
