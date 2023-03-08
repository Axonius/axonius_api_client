# -*- coding: utf-8 -*-
"""Test suite."""
import pytest

from axonius_api_client.api import json_api
from axonius_api_client.exceptions import ApiError, NotFoundError, ResponseNotOk
from axonius_api_client.tools import listify


class FixtureData:
    name = "badwolf"
    name_update = "badwolfxxx"
    names = [name, name_update]


class SystemRoles:
    @pytest.fixture(scope="class")
    def apiobj(self, api_system_roles):
        return api_system_roles

    def cleanup_roles(self, apiobj, value):
        for x in listify(value):
            try:
                apiobj.delete_by_name(name=x)
            except Exception:
                pass


class TestSystemRolesPrivate(SystemRoles):
    def test_get(self, apiobj):
        roles = apiobj._get()
        assert isinstance(roles, list) and roles
        for role in roles:
            assert isinstance(role, (json_api.system_roles.SystemRole,))

    def test_add_update_delete(self, apiobj):
        self.cleanup_roles(apiobj=apiobj, value=FixtureData.names)
        viewer = [x for x in apiobj._get() if x.name == "Viewer"][0]
        try:
            role = apiobj._add(
                name=FixtureData.name,
                permissions=viewer.permissions,
            )
        except ResponseNotOk:
            role = [x for x in apiobj._get() if x.name == FixtureData.name][0]

        assert isinstance(role, (json_api.system_roles.SystemRole,))

        assert role.name == FixtureData.name
        updated = apiobj._update(
            name=FixtureData.name_update, uuid=role.uuid, permissions=role.permissions
        )
        assert isinstance(updated, (json_api.system_roles.SystemRole,))
        assert updated.name == FixtureData.name_update

        try:
            deleted = apiobj._delete(uuid=role.uuid)
            assert isinstance(role, (json_api.system_roles.SystemRole,))
            assert deleted.document_meta == {"name": FixtureData.name_update}
        except ResponseNotOk:
            pass

        self.cleanup_roles(apiobj=apiobj, value=FixtureData.names)


class TestSystemRolesPublic(SystemRoles):
    def test_get(self, apiobj):
        roles = apiobj.get()
        assert isinstance(roles, list) and roles
        for role in roles:
            assert isinstance(role, dict)

    def test_add(self, apiobj):
        self.cleanup_roles(apiobj=apiobj, value=FixtureData.name)

        try:
            role = apiobj.add(name=FixtureData.name)
        except ResponseNotOk:
            role = apiobj.get_by_name(name=FixtureData.name)

        assert isinstance(role, dict) and role
        assert role["name"] == FixtureData.name
        self.cleanup_roles(apiobj=apiobj, value=FixtureData.name)

    def test_set_name(self, apiobj):
        self.cleanup_roles(apiobj=apiobj, value=FixtureData.names)

        try:
            role = apiobj.add(name=FixtureData.name)
        except ResponseNotOk:
            role = apiobj.get_by_name(name=FixtureData.name)

        updated = apiobj.set_name(name=role["name"], new_name=FixtureData.name_update)
        assert updated["name"] == FixtureData.name_update
        self.cleanup_roles(apiobj=apiobj, value=FixtureData.names)

    def test_set_perms(self, apiobj):
        self.cleanup_roles(apiobj=apiobj, value=FixtureData.name)

        try:
            role = apiobj.add(name=FixtureData.name)
        except ResponseNotOk:
            role = apiobj.get_by_name(name=FixtureData.name)

        updated = apiobj.set_perms(name=role["name"], users_assets="all", devices_assets="all")
        assert updated["permissions"]["adapters"]["get"] is False
        assert updated["permissions"]["users_assets"]["get"] is True
        assert updated["permissions"]["devices_assets"]["get"] is True

        updated2 = apiobj.set_perms(name=FixtureData.name, grant=False, users_assets="get")
        assert updated2["permissions"]["adapters"]["get"] is False
        assert updated2["permissions"]["users_assets"]["get"] is False
        assert updated2["permissions"]["devices_assets"]["get"] is True

        self.cleanup_roles(apiobj=apiobj, value=FixtureData.name)

    def test_add_already_exist(self, apiobj):
        existing = apiobj._get()[-1]
        with pytest.raises(ApiError):
            apiobj.add(name=existing.name)

    def test_get_by_uuid(self, apiobj):
        role = [x for x in apiobj.get()][0]
        reget = apiobj.get_by_uuid(uuid=role["uuid"])
        assert role == reget

    def test_get_by_name(self, apiobj):
        role = [x for x in apiobj.get()][0]
        reget = apiobj.get_by_name(name=role["name"])
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
            apiobj.set_name(name="XxXxX", new_name=role["name"])

    def test_set_name_same_name(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.set_name(name="XxXxX", new_name="XxXxX")

    def test_set_name_not_found(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.set_name(name="XxXxX", new_name="AAaAaA")

    def test_set_name_predefined(self, apiobj):
        role = [x for x in apiobj.get() if x.get("predefined")][0]
        with pytest.raises(ApiError):
            apiobj.set_name(name=role["name"], new_name="xXXxxXX")

    def test_pretty_perms(self, apiobj):
        role = apiobj.get()[0]
        value = apiobj.pretty_perms(role=role)
        assert isinstance(value, str)

    def test_cat_actions(self, apiobj):
        value = apiobj.cat_actions
        cats = value["categories"]
        acts = value["actions"]
        lens = value["lengths"]
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

    def test_cat_actions_to_perms_all_none(self, apiobj):
        perms = {"adapters": "none", "api_access": "all"}
        role_perms = apiobj.cat_actions_to_perms(**perms)
        for k, v in role_perms["adapters"].items():
            assert all([b is False for a, b in v.items()]) if isinstance(v, dict) else v is False
        for k, v in role_perms["api_access"].items():
            assert all([b is True for a, b in v.items()]) if isinstance(v, dict) else v is True

    def test_cat_actions_to_perms_all(self, apiobj):
        perms = {"adapters": "all"}
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
            role_perms=role_perms, adapters="get,put", grant=False
        )
        assert role_perms2["adapters"]["connections"]["post"] is True
        assert role_perms2["adapters"]["connections"]["put"] is True
        assert role_perms2["adapters"]["connections"]["delete"] is True
        assert role_perms2["adapters"]["get"] is False
        assert role_perms2["adapters"]["put"] is False

    def test_cat_actions_to_perms_bad_cat(self, apiobj):
        perms = {"XxXXx": "all"}
        with pytest.raises(ApiError) as exc:
            apiobj.cat_actions_to_perms(**perms)

        assert "Invalid category" in str(exc.value)

    def test_cat_actions_to_perms_bad_action(self, apiobj):
        perms = {"adapters": "xxxx"}
        with pytest.raises(ApiError) as exc:
            apiobj.cat_actions_to_perms(**perms)

        assert "Invalid action" in str(exc.value)
