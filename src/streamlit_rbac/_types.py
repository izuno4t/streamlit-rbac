"""streamlit-rbac の型定義."""

from collections.abc import Callable, Iterable
from typing import TypeAlias

RoleLoader: TypeAlias = Callable[[], Iterable[str]]
"""ユーザーのロール一覧を返す関数の型."""

OnDeniedHandler: TypeAlias = Callable[[], None]
"""権限拒否時に実行されるコールバック関数の型."""
