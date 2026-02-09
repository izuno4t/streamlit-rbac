# TASKS

Milestone: M1
Goal: streamlit-rbac v0.1.0 の全機能実装・テスト・品質チェック完了

## 目次

- [作業ルール](#作業ルール)
- [ステータス記法](#ステータス記法)
- [タスク一覧](#タスク一覧)
- [タスク詳細](#タスク詳細)
- [バックログ一覧](#バックログ一覧)

## 作業ルール

- タスク着手時にステータスを 🚧 に更新する
- タスク完了時にステータスを ✅ に更新する
- 依存先タスクがすべて ✅ になるまで着手しない

## ステータス記法

| ステータス | 意味 |
| ---- | ----- |
| ⏳ | 未着手 |
| 🚧 | 作業中 |
| 🧪 | レビュー |
| ✅ | 完了 |
| 🚫 | 取消 |

## タスク一覧

| ID | ステータス | 概要 | 依存先 |
| ---- | ---- | ---- | ---- |
| TASK-001 | ✅ | pyproject.tomlにstreamlit optional依存とメタデータを追記する | - |
| TASK-002 | ✅ | _types.pyに型エイリアス（RoleLoader, OnDeniedHandler）を定義する | - |
| TASK-003 | ✅ | _core.pyにロール判定関数（_resolve_roles, has_role, has_any_role, has_all_roles）を実装する | TASK-002 |
| TASK-004 | ✅ | test_core.pyにコア判定関数のパラメタライズドテストを作成する | TASK-003 |
| TASK-005 | ✅ | _decorators.pyに@require_rolesデコレータを実装する | TASK-003 |
| TASK-006 | ✅ | test_decorators.pyにデコレータのテストを作成する | TASK-005 |
| TASK-007 | ✅ | _streamlit.pyにauthorize_pageを実装する | TASK-003 |
| TASK-008 | ✅ | test_streamlit.pyにStreamlit統合層のモックテストを作成する | TASK-007 |
| TASK-009 | ✅ | __init__.pyに公開APIのre-exportとStreamlit遅延インポートを実装する | TASK-003,TASK-005,TASK-007 |
| TASK-010 | ✅ | 全テスト実行・カバレッジ90%以上・lint・型チェックを通過させる | TASK-004,TASK-006,TASK-008,TASK-009 |
| TASK-011 | ✅ | .pre-commit-config.yamlを作成しフックをインストールする | - |
| TASK-012 | ✅ | CI/CDパイプライン（GitHub Actions）を構築する | - |

## タスク詳細

### TASK-001

- 備考: descriptionとauthorsをプロジェクト実態に合わせる。`[project.optional-dependencies]`にstreamlitを追加する
- 注意: requires-pythonは現行の`>=3.11`を維持する

### TASK-003

- 備考: `_resolve_roles`は内部関数。frozensetを返す。user_rolesとrole_loaderの排他バリデーションを含む
- 注意: ロール文字列は大文字小文字を区別する

### TASK-005

- 備考: ParamSpec/TypeVarで元関数のシグネチャ型を保持する。on_deniedはPermissionError送出前に実行される副作用ハンドラ
- 注意: functools.wrapsで元関数のメタデータを保持すること

### TASK-007

- 備考: streamlitのimportは関数内で遅延実行する（optional dependency対応）
- 注意: authorize_pageは例外を送出せずst.error() + st.stop()で制御する

### TASK-009

- 備考: PEP 562の`__getattr__`でStreamlit関数を遅延インポートする。`__all__`を定義する
- 注意: _exceptions.pyは設計書に記載あるが中身は空のプレースホルダー。必要に応じて作成する

### TASK-010

- 備考: `uv run pytest --cov`、`uv run ruff check src tests`、`uv run mypy src`を全て通過させる
- 注意: カバレッジ90%以上が要件。不足時はテスト追加で対応する

## バックログ一覧

| ID | ステータス | 概要 | 依存先 |
| ---- | ---- | ---- | ---- |
| BACKLOG-001 | ✅ | PyPIへのパッケージ公開手順を整備する | - |
