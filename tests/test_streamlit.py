"""Streamlit統合のテスト."""
# ruff: noqa: PLC0415

from unittest.mock import MagicMock, patch


class TestSessionRoleLoader:
    def test_returns_roles_from_session(self) -> None:
        mock_st = MagicMock()
        mock_st.session_state = {"user_roles": ["Admin", "User"]}

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import session_role_loader

            loader = session_role_loader()
            assert loader() == ["Admin", "User"]

    def test_returns_empty_when_key_missing(self) -> None:
        mock_st = MagicMock()
        mock_st.session_state = {}

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import session_role_loader

            loader = session_role_loader()
            assert loader() == []

    def test_returns_empty_for_invalid_type(self) -> None:
        mock_st = MagicMock()
        mock_st.session_state = {"user_roles": "not_a_list"}

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import session_role_loader

            loader = session_role_loader()
            assert loader() == []

    def test_custom_session_key(self) -> None:
        mock_st = MagicMock()
        mock_st.session_state = {"my_roles": ["Editor"]}

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import session_role_loader

            loader = session_role_loader(session_key="my_roles")
            assert loader() == ["Editor"]


class TestUserAttrRoleLoader:
    def test_returns_roles_from_user_object(self) -> None:
        mock_st = MagicMock()
        user = MagicMock()
        user.roles = ["Admin"]
        mock_st.session_state = {"user": user}

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import user_attr_role_loader

            loader = user_attr_role_loader()
            assert loader() == ["Admin"]

    def test_returns_empty_when_user_missing(self) -> None:
        mock_st = MagicMock()
        mock_st.session_state = {}

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import user_attr_role_loader

            loader = user_attr_role_loader()
            assert loader() == []

    def test_returns_empty_when_attr_missing(self) -> None:
        mock_st = MagicMock()
        user = MagicMock(spec=[])
        mock_st.session_state = {"user": user}

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import user_attr_role_loader

            loader = user_attr_role_loader()
            assert loader() == []

    def test_returns_empty_for_invalid_type(self) -> None:
        mock_st = MagicMock()
        user = MagicMock()
        user.roles = "not_a_list"
        mock_st.session_state = {"user": user}

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import user_attr_role_loader

            loader = user_attr_role_loader()
            assert loader() == []


class TestGuardPage:
    def test_allowed(self) -> None:
        mock_st = MagicMock()

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import guard_page

            guard_page("Admin", role_loader=lambda: ["Admin"])
            mock_st.error.assert_not_called()
            mock_st.stop.assert_not_called()

    def test_denied(self) -> None:
        mock_st = MagicMock()

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import guard_page

            guard_page("Admin", role_loader=lambda: ["User"])
            mock_st.error.assert_called_once()
            mock_st.stop.assert_called_once()

    def test_unauthenticated_with_login_url(self) -> None:
        mock_st = MagicMock()

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import guard_page

            guard_page("Admin", role_loader=lambda: [], login_url="/login")
            mock_st.warning.assert_called_once()
            mock_st.link_button.assert_called_once_with("ログインページへ", "/login")
            mock_st.stop.assert_called_once()

    def test_unauthenticated_without_login_url(self) -> None:
        mock_st = MagicMock()

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import guard_page

            guard_page("Admin", role_loader=lambda: [])
            mock_st.error.assert_called_once_with("ログインが必要です。")
            mock_st.stop.assert_called_once()

    def test_custom_denied_message(self) -> None:
        mock_st = MagicMock()

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import guard_page

            guard_page(
                "Admin",
                role_loader=lambda: ["User"],
                denied_message="アクセス拒否",
            )
            mock_st.error.assert_called_once_with("アクセス拒否")

    def test_multiple_roles_allowed(self) -> None:
        mock_st = MagicMock()

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import guard_page

            guard_page("Admin", "Manager", role_loader=lambda: ["Manager"])
            mock_st.error.assert_not_called()
            mock_st.stop.assert_not_called()

    def test_custom_user_session_key_and_role_attr(self) -> None:
        mock_st = MagicMock()
        user = MagicMock()
        user.granted_roles = ["Editor"]
        mock_st.session_state = {"current_user": user}

        with patch.dict("sys.modules", {"streamlit": mock_st}):
            from streamlit_rbac._streamlit import user_attr_role_loader

            loader = user_attr_role_loader(
                user_session_key="current_user", role_attr="granted_roles"
            )
            assert loader() == ["Editor"]
