# -*- coding: utf-8 -*-
"""Test suite."""

import pytest

from axonius_api_client.exceptions import ApiError, NotFoundError

from ...meta import TEST_USER


@pytest.mark.skip("Waiting for update to 3.3!")  # XXX update public API for roles/users
class TestSystemUsers:
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_system):
        """Pass."""
        return api_system.users

    def test__get(self, apiobj):
        """Pass."""
        data = apiobj._get()
        assert isinstance(data, list)
        for x in data:
            assert isinstance(x, dict)

    def test__get_limit(self, apiobj):
        """Pass."""
        data = apiobj._get(limit=1)
        assert isinstance(data, list)
        for x in data:
            assert isinstance(x, dict)
        assert len(data) == 1

    def test__get_limit_skip(self, apiobj):
        """Pass."""
        all_data = apiobj._get()
        data = apiobj._get(limit=1, skip=1)
        assert isinstance(data, list)
        for x in data:
            assert isinstance(x, dict)
        if len(all_data) == 1:
            assert len(data) == 0
        else:
            assert len(data) == 1

    def test_add_get_update_delete(self, apiobj):
        """Pass."""
        try:
            apiobj.get(name=TEST_USER)
        except NotFoundError:
            pass
        else:
            apiobj.delete(name=TEST_USER)

        added = apiobj.add(name=TEST_USER, password=TEST_USER)
        assert isinstance(added, dict)
        assert added["user_name"] == TEST_USER
        assert not added["first_name"]
        assert not added["last_name"]
        assert added["password"] == ["unchanged"]

        with pytest.raises(ApiError):
            apiobj.add(name=TEST_USER, password=TEST_USER)

        updated = apiobj.update(
            name=TEST_USER,
            firstname=TEST_USER,
            lastname=TEST_USER,
            password=TEST_USER + "X",
        )
        assert isinstance(updated, dict)
        assert updated["user_name"] == TEST_USER
        assert updated["first_name"] == TEST_USER
        assert updated["last_name"] == TEST_USER
        assert updated["password"] == ["unchanged"]

        roles = apiobj.parent.roles.get()
        rolename = roles[-1]["name"]
        updated_role = apiobj.update_role(name=TEST_USER, rolename=rolename)
        assert updated_role["role_name"] == rolename

        deleted = apiobj.delete(name=TEST_USER)
        assert isinstance(deleted, list)
        assert not [x for x in deleted if x["uuid"] == added["uuid"]]

        with pytest.raises(ApiError):
            apiobj.update(name=TEST_USER)

        with pytest.raises(NotFoundError):
            apiobj.get(name=TEST_USER)

    def test_add_bad_role(self, apiobj):
        """Pass."""
        val = "xxx"
        with pytest.raises(NotFoundError):
            apiobj.add(name=val, password=val, rolename="flimflam")
