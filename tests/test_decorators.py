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

    def test_with_role_loader_allowed(self) -> None:
        @require_roles("Admin", role_loader=lambda: ["Admin"])
        def action() -> str:
            return "ok"

        assert action() == "ok"

    def test_with_role_loader_denied(self) -> None:
        @require_roles("Admin", role_loader=lambda: ["User"])
        def action() -> str:
            return "ok"

        with pytest.raises(PermissionError):
            action()

    def test_denied_message_contains_role(self) -> None:
        @require_roles("Admin", "Manager", user_roles=["User"])
        def action() -> str:
            return "ok"

        with pytest.raises(PermissionError, match="Admin"):
            action()
