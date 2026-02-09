"""__init__.py の公開APIと遅延importのテスト."""
# ruff: noqa: PLC0415

import pytest

import streamlit_rbac


class TestPublicApi:
    def test_version(self) -> None:
        assert hasattr(streamlit_rbac, "__version__")
        assert isinstance(streamlit_rbac.__version__, str)

    def test_core_functions_importable(self) -> None:
        from streamlit_rbac import has_all_roles, has_any_role, has_role

        assert callable(has_role)
        assert callable(has_any_role)
        assert callable(has_all_roles)

    def test_decorator_importable(self) -> None:
        from streamlit_rbac import require_roles

        assert callable(require_roles)

    def test_types_importable(self) -> None:
        from streamlit_rbac import OnDeniedHandler, RoleLoader

        assert OnDeniedHandler is not None
        assert RoleLoader is not None


class TestLazyImport:
    def test_guard_page_importable(self) -> None:
        from streamlit_rbac import guard_page

        assert callable(guard_page)

    def test_session_role_loader_importable(self) -> None:
        from streamlit_rbac import session_role_loader

        assert callable(session_role_loader)

    def test_user_attr_role_loader_importable(self) -> None:
        from streamlit_rbac import user_attr_role_loader

        assert callable(user_attr_role_loader)

    def test_invalid_attribute_raises_error(self) -> None:
        with pytest.raises(AttributeError, match="no_such_function"):
            streamlit_rbac.no_such_function  # noqa: B018
