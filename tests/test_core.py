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
        loader = lambda: ["Admin", "User"]  # noqa: E731
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

    def test_with_role_loader(self) -> None:
        loader = lambda: ["Manager"]  # noqa: E731
        assert has_any_role("Admin", "Manager", role_loader=loader) is True

    def test_with_role_loader_no_match(self) -> None:
        loader = lambda: ["User"]  # noqa: E731
        assert has_any_role("Admin", "Manager", role_loader=loader) is False


class TestHasAllRoles:
    def test_all_present(self) -> None:
        assert (
            has_all_roles("Admin", "Auditor", user_roles=["Admin", "Auditor"]) is True
        )

    def test_partial(self) -> None:
        assert has_all_roles("Admin", "Auditor", user_roles=["Admin"]) is False

    def test_superset(self) -> None:
        assert (
            has_all_roles("Admin", "Auditor", user_roles=["Admin", "Auditor", "User"])
            is True
        )

    def test_empty_required(self) -> None:
        assert has_all_roles(user_roles=["Admin"]) is True

    def test_with_role_loader(self) -> None:
        loader = lambda: ["Admin", "Auditor"]  # noqa: E731
        assert has_all_roles("Admin", "Auditor", role_loader=loader) is True

    def test_with_role_loader_partial(self) -> None:
        loader = lambda: ["Admin"]  # noqa: E731
        assert has_all_roles("Admin", "Auditor", role_loader=loader) is False
