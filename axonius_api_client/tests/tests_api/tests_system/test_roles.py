# -*- coding: utf-8 -*-
"""Test suite."""

# import pytest
# from axonius_api_client.constants import DEFAULT_PERM
# from axonius_api_client.exceptions import ApiError, NotFoundError

# from ...meta import TEST_PERM, TEST_ROLE

'''
@pytest.mark.skip("Waiting for update to 3.3!")  # XXX update public API for roles/users
class TestSystemRoles:
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_system):
        """Pass."""
        return api_system.roles

    def test__get(self, apiobj):
        """Pass."""
        data = apiobj._get()
        assert isinstance(data, list)
        for x in data:
            assert isinstance(x, dict)

    def test_get_set_default(self, apiobj):
        """Pass."""
        roles = apiobj.get()
        current_role = apiobj.get_default()
        assert isinstance(current_role, dict)

        new_roles = [x for x in roles if x["name"] != current_role["name"]]
        if new_roles:
            new_role = new_roles[0]["name"]
            updated_role = apiobj.set_default(new_role)
            assert isinstance(updated_role, dict)
            assert updated_role["name"] == new_role

    def test_add_invalid_perm(self, apiobj):
        """Pass."""
        with pytest.raises(ApiError):
            apiobj.add("x", "badwolf_itai")

    def test_add_get_update_delete(self, apiobj):
        """Pass."""
        try:
            apiobj.get(name=TEST_ROLE)
        except NotFoundError:
            pass
        else:
            apiobj.delete(name=TEST_ROLE)

        added = apiobj.add(name=TEST_ROLE)
        assert isinstance(added, dict)
        assert added["name"] == TEST_ROLE
        assert isinstance(added["permissions"], dict)

        with pytest.raises(ApiError):
            apiobj.add(name=TEST_ROLE)

        added_permissions = added["permissions"]
        update_permissions = {}

        for k, v in added_permissions.items():
            assert v == DEFAULT_PERM
            update_permissions[k.lower()] = TEST_PERM

        updated = apiobj.update(name=TEST_ROLE, **update_permissions)
        assert isinstance(updated, dict)

        updated_permissions = updated["permissions"]
        for k, v in updated_permissions.items():
            assert v == TEST_PERM

        deleted = apiobj.delete(name=TEST_ROLE)
        assert isinstance(deleted, list)
        assert not [x for x in deleted if x["name"] == added["name"]]

        with pytest.raises(NotFoundError):
            apiobj.update(name=TEST_ROLE)

        with pytest.raises(NotFoundError):
            apiobj.delete(name=TEST_ROLE)

        with pytest.raises(NotFoundError):
            apiobj.get(name=TEST_ROLE)
'''
