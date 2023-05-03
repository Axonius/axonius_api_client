# -*- coding: utf-8 -*-
"""Test suite."""
import pytest

from axonius_api_client.api import DataScopes, SystemRoles, json_api
from axonius_api_client.exceptions import ApiError, NotFoundError
from axonius_api_client.tools import listify


class FixtureData:
    name = "badwolf data scope"
    name_update = f"{name} UPDATED"
    names = [name, name_update]
    description = "it bad wolfy"
    description_update = f"{description} UPDATED"
    asset_scope_devices1 = "badwolf asset scope for devices 1"
    asset_scope_devices2 = "badwolf asset scope for devices 2"
    asset_scope_users1 = "badwolf asset scope for users 1"
    asset_scope_users2 = "badwolf asset scope for users 2"
    asset_scopes_devices = [asset_scope_devices1, asset_scope_devices2]
    asset_scopes_users = [asset_scope_users1, asset_scope_users2]
    role = "badwolf role using data scope"


class DataScopeFixtures:
    def cleanup_data_scopes(self, apiobj, value):
        for x in listify(value):
            try:
                apiobj.delete(value=x)
            except ApiError:
                pass

    def cleanup_asset_scopes(self, apiasset, value):
        try:
            apiasset.saved_query.delete(rows=value, errors=False)
        except ApiError:
            pass

    def cleanup_roles(self, apiobj, value):
        if isinstance(apiobj, SystemRoles):
            api_system_roles = apiobj
        elif isinstance(apiobj, DataScopes):
            api_system_roles = apiobj.system_roles

        for x in listify(value):
            try:
                api_system_roles.delete_by_name(name=x)
            except ApiError:
                pass

    def create_data_scope(self, apiobj, name, device_scopes, user_scopes):
        self.cleanup_data_scopes(apiobj=apiobj, value=name)

        row = apiobj.create(
            name=FixtureData.name,
            description=FixtureData.description,
            device_scopes=device_scopes,
            user_scopes=user_scopes,
        )

        assert str(row)
        assert repr(row)
        assert isinstance(row.updated_user_first_name, str)
        assert isinstance(row.updated_user_last_name, str)
        assert isinstance(row.updated_user_full_name, str)

        yield row

        self.cleanup_data_scopes(apiobj=apiobj, value=row.uuid)

    def create_asset_scope(self, apiasset, name):
        if not apiasset.data_scopes.is_feature_enabled:
            pytest.skip("Data Scopes Feature Flag not enabled")
        self.cleanup_asset_scopes(apiasset=apiasset, value=name)

        row = apiasset.saved_query.add(
            name=name,
            asset_scope=True,
            as_dataclass=True,
        )

        yield row

        self.cleanup_asset_scopes(apiasset=apiasset, value=row.uuid)

    @pytest.fixture(scope="class")
    def f_data_scope(self, api_data_scopes, f_asset_scope_devices1, f_asset_scope_users1):
        if not api_data_scopes.is_feature_enabled:
            pytest.skip("Data Scopes Feature Flag not enabled")

        yield from self.create_data_scope(
            apiobj=api_data_scopes,
            name=FixtureData.name,
            device_scopes=f_asset_scope_devices1,
            user_scopes=f_asset_scope_users1,
        )

    @pytest.fixture(scope="class")
    def f_asset_scope_devices1(self, api_data_scopes):
        if not api_data_scopes.is_feature_enabled:
            pytest.skip("Data Scopes Feature Flag not enabled")

        yield from self.create_asset_scope(
            apiasset=api_data_scopes.devices, name=FixtureData.asset_scope_devices1
        )

    @pytest.fixture(scope="class")
    def f_asset_scope_devices2(self, api_data_scopes):
        if not api_data_scopes.is_feature_enabled:
            pytest.skip("Data Scopes Feature Flag not enabled")

        yield from self.create_asset_scope(
            apiasset=api_data_scopes.devices, name=FixtureData.asset_scope_devices2
        )

    @pytest.fixture(scope="class")
    def f_asset_scope_users1(self, api_data_scopes):
        if not api_data_scopes.is_feature_enabled:
            pytest.skip("Data Scopes Feature Flag not enabled")

        yield from self.create_asset_scope(
            apiasset=api_data_scopes.users, name=FixtureData.asset_scope_users1
        )

    @pytest.fixture(scope="class")
    def f_asset_scope_users2(self, api_data_scopes):
        if not api_data_scopes.is_feature_enabled:
            pytest.skip("Data Scopes Feature Flag not enabled")

        yield from self.create_asset_scope(
            apiasset=api_data_scopes.users, name=FixtureData.asset_scope_users2
        )


class DataScopesBase(DataScopeFixtures):
    @pytest.fixture(scope="class")
    def apiobj(self, api_data_scopes):
        if not api_data_scopes.is_feature_enabled:
            pytest.skip("Data Scopes Feature Flag not enabled")
        self.cleanup_data_scopes(apiobj=api_data_scopes, value=FixtureData.names)
        self.cleanup_asset_scopes(
            apiasset=api_data_scopes.users, value=FixtureData.asset_scopes_users
        )
        self.cleanup_asset_scopes(
            apiasset=api_data_scopes.devices, value=FixtureData.asset_scopes_devices
        )
        return api_data_scopes


class TestDataScopesPublic(DataScopesBase):
    def test_get(self, apiobj, f_data_scope):
        items = apiobj.get()
        assert isinstance(items, list) and items
        for item in items:
            assert isinstance(item, json_api.data_scopes.DataScope)

    def test_get_safe(self, api_data_scopes):
        items = api_data_scopes.get_safe()
        assert isinstance(items, list)

    def test_get_value_name(self, apiobj, f_data_scope):
        item = apiobj.get(value=f_data_scope.name)
        assert isinstance(item, json_api.data_scopes.DataScope)
        assert item.name == f_data_scope.name

    def test_get_value_uuid(self, apiobj, f_data_scope):
        item = apiobj.get(value=f_data_scope.uuid)
        assert isinstance(item, json_api.data_scopes.DataScope)
        assert item.name == f_data_scope.name

    def test_get_value_fail(self, apiobj, f_data_scope):
        with pytest.raises(NotFoundError):
            apiobj.get(value="I DO NOT EXISTSSSS")

    def test_update_name(self, apiobj, f_data_scope):
        item = apiobj.update_name(value=f_data_scope, update=FixtureData.name_update)
        assert item.name == FixtureData.name_update

    def test_update_description(self, apiobj, f_data_scope):
        item = apiobj.update_description(value=f_data_scope, update=FixtureData.description_update)
        assert item.description == FixtureData.description_update

    def test_update_name_fail(self, apiobj, f_data_scope):
        with pytest.raises(ApiError):
            apiobj.update_name(value=f_data_scope.name, update=f_data_scope.name)

    def test_create_fail_no_scopes(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.create(name="d i r t")

    def test_update_user_scopes(self, apiobj, f_data_scope, f_asset_scope_users2):
        original_queries = f_data_scope.users_queries
        item = apiobj.update_user_scopes(
            value=f_data_scope, update=f_asset_scope_users2.name, append=True
        )
        assert item.users_queries == original_queries + [f_asset_scope_users2.uuid]

        item = apiobj.update_user_scopes(
            value=f_data_scope, update=f_asset_scope_users2.name, remove=True
        )
        assert f_asset_scope_users2.uuid not in item.users_queries

        item = apiobj.update_user_scopes(value=f_data_scope, update=original_queries)
        assert item.users_queries == original_queries

    def test_update_user_scopes_fail_empty_init(self, apiobj, f_data_scope):
        with pytest.raises(ApiError):
            apiobj.update_user_scopes(value=f_data_scope, update=[])

    def test_update_user_scopes_fail_empty_update(self, apiobj, f_data_scope, monkeypatch):
        monkeypatch.setattr(f_data_scope, "devices_queries", [])
        with pytest.raises(ApiError):
            f_data_scope.update_scopes(
                scope_type="users", scopes=f_data_scope.users_scopes, remove=True
            )

    def test_update_device_scopes(self, apiobj, f_data_scope, f_asset_scope_devices2):
        original_queries = f_data_scope.devices_queries
        item = apiobj.update_device_scopes(
            value=f_data_scope, update=f_asset_scope_devices2.name, append=True
        )
        assert item.devices_queries == original_queries + [f_asset_scope_devices2.uuid]

        item = apiobj.update_device_scopes(
            value=f_data_scope, update=f_asset_scope_devices2.name, remove=True
        )
        assert f_asset_scope_devices2.uuid not in item.devices_queries

        item = apiobj.update_device_scopes(value=f_data_scope, update=original_queries)
        assert item.devices_queries == original_queries

    def test_update_device_scopes_fail_empty_init(self, apiobj, f_data_scope):
        with pytest.raises(ApiError):
            apiobj.update_device_scopes(value=f_data_scope, update=[])

    def test_update_device_scopes_fail_empty_update(self, apiobj, f_data_scope, monkeypatch):
        monkeypatch.setattr(f_data_scope, "users_queries", [])
        with pytest.raises(ApiError):
            f_data_scope.update_scopes(
                scope_type="devices", scopes=f_data_scope.devices_scopes, remove=True
            )

    def test_build_role_data_scope(self, apiobj, f_data_scope):
        exp = {"enabled": True, "data_scope": f_data_scope.uuid}
        data = apiobj.build_role_data_scope(value=f_data_scope, required=True)
        assert data == exp

    def test_build_role_data_scope_required(self, api_data_scopes):
        with pytest.raises(ApiError):
            api_data_scopes.build_role_data_scope(value=None, required=True)

    def test_build_role_data_scope_not_required(self, api_data_scopes):
        exp = {"enabled": False, "data_scope": None}
        data = api_data_scopes.build_role_data_scope(value=None, required=False)
        assert data == exp

    def test_role_add_data_scope(self, apiobj, f_data_scope):
        self.cleanup_roles(apiobj=apiobj, value=FixtureData.role)
        exp = {"enabled": True, "data_scope": f_data_scope.uuid}
        role = apiobj.system_roles.add(name=FixtureData.role, data_scope=f_data_scope)
        assert role["data_scope_restriction"] == exp
        self.cleanup_roles(apiobj=apiobj, value=FixtureData.role)

    def test_role_update_data_scope(self, apiobj, f_data_scope):
        self.cleanup_roles(apiobj=apiobj, value=FixtureData.role)

        exp = {"enabled": False, "data_scope": None}
        role = apiobj.system_roles.add(name=FixtureData.role)
        assert role["data_scope_restriction"] == exp

        exp = {"enabled": True, "data_scope": f_data_scope.uuid}
        role = apiobj.system_roles.update_data_scope(name=FixtureData.role, data_scope=f_data_scope)
        assert role["data_scope_restriction"] == exp

        exp = {"enabled": False, "data_scope": None}
        role = apiobj.system_roles.update_data_scope(name=FixtureData.role, remove=True)
        assert role["data_scope_restriction"] == exp

        self.cleanup_roles(apiobj=apiobj, value=FixtureData.role)
