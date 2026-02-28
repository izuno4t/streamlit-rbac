"""Streamlit統合のテスト."""
# ruff: noqa: PLC0415

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
            mock_st.link_button.assert_called_once_with("ログインページへ", "/login")
            mock_st.stop.assert_called_once()

    def test_unauthenticated_without_login_url(self) -> None:
        mock_st = MagicMock()

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import authorize_page

            authorize_page("Admin", role_loader=lambda: [])
            mock_st.error.assert_called_once_with("ログインが必要です。")
            mock_st.stop.assert_called_once()

    def test_custom_denied_message(self) -> None:
        mock_st = MagicMock()

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import authorize_page

            authorize_page(
                "Admin",
                role_loader=lambda: ["User"],
                denied_message="アクセス拒否",
            )
            mock_st.error.assert_called_once_with("アクセス拒否")

    def test_multiple_roles_allowed(self) -> None:
        mock_st = MagicMock()

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import authorize_page

            authorize_page("Admin", "Manager", role_loader=lambda: ["Manager"])
            mock_st.error.assert_not_called()
            mock_st.stop.assert_not_called()

    def test_empty_allowed_roles_raises_value_error(self) -> None:
        from streamlit_rbac._streamlit import authorize_page

        with pytest.raises(ValueError, match="allowed_roles must not be empty"):
            authorize_page(role_loader=lambda: ["Admin"])

    def test_role_loader_exception_propagation(self) -> None:
        mock_st = MagicMock()

        def bad_loader() -> list[str]:
            raise RuntimeError("loader failed")

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import authorize_page

            with pytest.raises(RuntimeError, match="loader failed"):
                authorize_page("Admin", role_loader=bad_loader)
