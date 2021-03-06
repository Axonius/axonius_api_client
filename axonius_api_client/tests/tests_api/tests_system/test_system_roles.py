# -*- coding: utf-8 -*-
"""Test suite."""
import pytest

from axonius_api_client.constants.system import Role
from axonius_api_client.exceptions import ApiError, NotFoundError

NAME = "badwolf"
NEW_NAME = "badwolfxxx"


def cleanup(apiobj):
    try:
        apiobj.delete_by_name(name=NAME)
    except Exception:
        pass

    try:
        apiobj.delete_by_name(name=NEW_NAME)
    except Exception:
        pass


class TestSystemRolesPrivate:
    @pytest.fixture(scope="class")
    def apiobj(self, api_system_roles):
        return api_system_roles

    def test_get(self, apiobj):
        roles = apiobj._get()
        assert isinstance(roles, list) and roles
        for role in roles:
            assert isinstance(role, dict)

    def test_add_update_delete(self, apiobj):
        cleanup(apiobj)
        role = apiobj._add(name=NAME, permissions={})
        assert role[Role.NAME] == NAME
        updated = apiobj._update(name=NEW_NAME, uuid=role[Role.UUID], permissions=role[Role.PERMS])
        assert updated[Role.NAME] == NEW_NAME

        deleted = apiobj._delete(uuid=role[Role.UUID])
        assert deleted == {Role.NAME: NEW_NAME}
        cleanup(apiobj)


class TestSystemRolesPublic:
    @pytest.fixture(scope="class")
    def apiobj(self, api_system_roles):
        return api_system_roles

    def test_get(self, apiobj):
        roles = apiobj.get()
        assert isinstance(roles, list) and roles
        for role in roles:
            assert isinstance(role, dict)

    def test_add(self, apiobj):
        cleanup(apiobj)

        role = apiobj.add(name=NAME)
        assert isinstance(role, dict) and role
        assert role[Role.NAME] == NAME
        cleanup(apiobj)

    def test_set_name(self, apiobj):
        cleanup(apiobj)

        apiobj.add(name=NAME)
        updated = apiobj.set_name(name=NAME, new_name=NEW_NAME)
        assert updated[Role.NAME] == NEW_NAME
        cleanup(apiobj)

    def test_set_perms(self, apiobj):
        cleanup(apiobj)

        apiobj.add(name=NAME)
        updated = apiobj.set_perms(name=NAME, users_assets=Role.ALL, devices_assets=Role.ALL)
        assert updated[Role.PERMS]["adapters"]["get"] is False
        assert updated[Role.PERMS]["users_assets"]["get"] is True
        assert updated[Role.PERMS]["devices_assets"]["get"] is True

        updated2 = apiobj.set_perms(name=NAME, grant=False, users_assets="get")
        assert updated2[Role.PERMS]["adapters"]["get"] is False
        assert updated2[Role.PERMS]["users_assets"]["get"] is False
        assert updated2[Role.PERMS]["devices_assets"]["get"] is True

        cleanup(apiobj)

    def test_set_perms_no_changes(self, apiobj):
        cleanup(apiobj)

        apiobj.add(name=NAME)
        with pytest.raises(ApiError) as exc:
            apiobj.set_perms(name=NAME)

        assert "No permission changes" in str(exc.value)
        cleanup(apiobj)

    def test_add_already_exist(self, apiobj):
        cleanup(apiobj)
        apiobj.add(name=NAME)

        with pytest.raises(ApiError):
            apiobj.add(name=NAME)

        cleanup(apiobj)

    def test_get_by_uuid(self, apiobj):
        role = [x for x in apiobj.get()][0]
        reget = apiobj.get_by_uuid(uuid=role[Role.UUID])
        assert role == reget

    def test_get_by_name(self, apiobj):
        role = [x for x in apiobj.get()][0]
        reget = apiobj.get_by_name(name=role[Role.NAME])
        assert role == reget

    def test_get_by_uuid_not_found(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get_by_uuid(uuid="XxXxX")

    def test_get_by_name_not_found(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get_by_name(name="XxXxX")

    def test_set_name_already_exists(self, apiobj):
        roles = apiobj.get()
        role = roles[0]
        with pytest.raises(ApiError):
            apiobj.set_name(name="XxXxX", new_name=role[Role.NAME])

    def test_set_name_same_name(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.set_name(name="XxXxX", new_name="XxXxX")

    def test_set_name_not_found(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.set_name(name="XxXxX", new_name="AAaAaA")

    def test_set_name_predefined(self, apiobj):
        role = [x for x in apiobj.get() if x.get("predefined")][0]
        with pytest.raises(ApiError):
            apiobj.set_name(name=role[Role.NAME], new_name="xXXxxXX")

    def test_pretty_perms(self, apiobj):
        role = apiobj.get()[0]
        value = apiobj.pretty_perms(role=role)
        assert isinstance(value, str)

    def test_cat_actions(self, apiobj):
        value = apiobj.cat_actions
        cats = value[Role.CATS]
        acts = value[Role.ACTS]
        lens = value[Role.LENS]
        assert isinstance(value, dict)
        assert isinstance(cats, dict) and cats
        assert isinstance(acts, dict) and acts
        assert isinstance(lens, dict) and lens
        for k, v in cats.items():
            assert isinstance(k, str) and k
            assert isinstance(v, str) and v

        for k, v in lens.items():
            assert isinstance(k, str) and k
            assert isinstance(v, int) and v

        for k, v in acts.items():
            assert isinstance(k, str) and k
            assert isinstance(v, dict) and v
            for a, b in v.items():
                assert isinstance(a, str) and a
                assert isinstance(b, str) and b

    def test_cat_actions_to_perms_all(self, apiobj):
        perms = {"adapters": Role.ALL}
        role_perms = apiobj.cat_actions_to_perms(**perms)
        for k, v in role_perms.items():
            if k in perms:
                for a, b in v.items():
                    if isinstance(b, dict):
                        for c, d in b.items():
                            assert d is True
                    else:
                        assert b is True
            else:
                for a, b in v.items():
                    if isinstance(b, dict):
                        for c, d in b.items():
                            assert d is False
                    else:
                        assert b is False

        role_perms2 = apiobj.cat_actions_to_perms(
            role_perms=role_perms, adapters="get,post", grant=False
        )
        assert role_perms2["adapters"]["connections"]["post"] is True
        assert role_perms2["adapters"]["connections"]["put"] is True
        assert role_perms2["adapters"]["connections"]["delete"] is True
        assert role_perms2["adapters"]["get"] is False
        assert role_perms2["adapters"]["post"] is False

    def test_cat_actions_to_perms_bad_cat(self, apiobj):
        perms = {"XxXXx": Role.ALL}
        with pytest.raises(ApiError) as exc:
            apiobj.cat_actions_to_perms(**perms)

        assert "Invalid category" in str(exc.value)

    def test_cat_actions_to_perms_bad_action(self, apiobj):
        perms = {"adapters": "xxxx"}
        with pytest.raises(ApiError) as exc:
            apiobj.cat_actions_to_perms(**perms)

        assert "Invalid action" in str(exc.value)
