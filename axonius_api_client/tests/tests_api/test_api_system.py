# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

import axonius_api_client as axonapi
from axonius_api_client import exceptions, tools

from .. import utils, meta


@pytest.fixture(scope="module")
def apiobj(request):
    """Pass."""
    auth = utils.get_auth(request)

    api = axonapi.System(auth=auth)

    # INSTANCES
    with pytest.warns(exceptions.BetaWarning):
        utils.check_apiobj_children(apiobj=api, instances=axonapi.api.system.Instances)

    # DISCOVER
    utils.check_apiobj_children(apiobj=api, discover=axonapi.api.system.Discover)

    # META
    utils.check_apiobj_children(apiobj=api, meta=axonapi.api.system.Meta)

    # USERS
    utils.check_apiobj_children(apiobj=api, users=axonapi.api.system.Users)

    # ROLES
    utils.check_apiobj_children(apiobj=api, roles=axonapi.api.system.Roles)

    # SETTINGS
    with pytest.warns(exceptions.BetaWarning):
        utils.check_apiobj_children(apiobj=api, settings=axonapi.api.system.Settings)

    utils.check_apiobj_children(
        apiobj=api.settings, lifecycle=axonapi.api.system.SettingsLifecycle
    )
    utils.check_apiobj_children(apiobj=api.settings, gui=axonapi.api.system.SettingsGui)
    utils.check_apiobj_children(
        apiobj=api.settings, core=axonapi.api.system.SettingsCore
    )

    utils.check_apiobj(authobj=auth, apiobj=api)

    return api


class TestSystemDiscover(object):
    """Pass."""

    @pytest.fixture(scope="class")
    def childobj(self, apiobj):
        """Pass."""
        return apiobj.discover

    def test_lifecycle(self, childobj):
        """Pass."""
        lifecycle = childobj.lifecycle()
        assert isinstance(lifecycle, dict)
        assert "status" in lifecycle
        assert lifecycle["status"] in ["starting", "running", "done"]

    def test__lifecycle(self, childobj):
        """Pass."""
        lifecycle = childobj._lifecycle()
        assert isinstance(lifecycle, dict)
        assert "status" in lifecycle
        assert lifecycle["status"] in ["starting", "running", "done"]

    def test_start_stop_lifecycle(self, childobj):
        """Pass."""
        if childobj.is_running:
            stopped = childobj.stop()
            assert isinstance(stopped, dict)
            assert stopped["status"] == "done"

        started = childobj.start()
        assert isinstance(started, dict)
        assert started["status"] in ["starting", "running"]

        re_stopped = childobj.stop()
        assert isinstance(re_stopped, dict)
        assert re_stopped["status"] == "done"


class TestSystemMeta(object):
    """Pass."""

    @pytest.fixture(scope="class")
    def childobj(self, apiobj):
        """Pass."""
        return apiobj.meta

    def val_entity_sizes(self, data):
        """Pass."""
        avg_document_size = data("avg_document_size")
        assert isinstance(avg_document_size, tools.INT)
        capped = data("capped")
        assert isinstance(capped, tools.INT)
        entities_last_point = data("entities_last_point")
        assert isinstance(entities_last_point, tools.INT)
        size = data("size")
        assert isinstance(size, tools.INT)
        assert not data

    def val_historical_sizes(self, data):
        """Pass."""
        disk_free = data.pop("disk_free")
        assert isinstance(disk_free, tools.INT) and disk_free

        disk_used = data.pop("disk_used")
        assert isinstance(disk_used, tools.INT) and disk_used

        entity_sizes = data.pop("entity_sizes")
        assert isinstance(entity_sizes, dict) and entity_sizes

        users = entity_sizes.pop("Users")
        assert isinstance(users, dict) and users

        devices = entity_sizes.pop("Devices")
        assert isinstance(devices, dict) and devices
        assert not entity_sizes
        assert not data

    def val_about(self, data):
        """Pass."""
        assert isinstance(data, dict)

        keys = ["Build Date", "Commit Date", "Commit Hash", "Version"]
        empty_ok = ["Version"]

        for key in keys:
            assert key in data
            assert isinstance(data[key], tools.STR)
            if key not in empty_ok:
                assert data[key]

    def test_about(self, childobj):
        """Pass."""
        data = childobj.about()
        self.val_about(data)

    def test__about(self, childobj):
        """Pass."""
        data = childobj._about()
        self.val_about(data)

    def test_historical_sizes(self, childobj):
        """Pass."""
        data = childobj.historical_sizes()
        self.val_historical_sizes(data)

    def test__historical_sizes(self, childobj):
        """Pass."""
        data = childobj._historical_sizes()
        self.val_historical_sizes(data)


class SettingChild(object):
    """Pass."""

    def test_get(self, childobj):
        """Pass."""
        settings = childobj.get()
        assert isinstance(settings, dict)

    def test__get(self, childobj):
        """Pass."""
        settings = childobj._get()
        assert isinstance(settings, dict)
        assert "config" in settings
        assert isinstance(settings["config"], dict)
        assert "schema" in settings
        assert isinstance(settings["schema"], dict)

    def test_update(self, childobj):
        """Pass."""
        settings = childobj.get()
        updated_settings = childobj.update(config=settings)
        assert settings == updated_settings

    def test__update(self, childobj):
        """Pass."""
        settings = childobj.get()
        ret = childobj._update(config=settings)
        assert not ret


class TestSystemSettingsGui(SettingChild):
    """Pass."""

    @pytest.fixture(scope="class")
    def childobj(self, apiobj):
        """Pass."""
        return apiobj.settings.gui


class TestSystemSettingsLifecycle(SettingChild):
    """Pass."""

    @pytest.fixture(scope="class")
    def childobj(self, apiobj):
        """Pass."""
        return apiobj.settings.lifecycle


class TestSystemSettingsCore(SettingChild):
    """Pass."""

    @pytest.fixture(scope="class")
    def childobj(self, apiobj):
        """Pass."""
        return apiobj.settings.core


class TestSystemAggregation(object):
    """Pass."""

    @pytest.fixture(scope="class")
    def childobj(self, apiobj):
        """Pass."""
        return apiobj.settings.core.aggregation

    def test_get(self, childobj):
        """Pass."""
        settings = childobj.get()
        assert isinstance(settings.pop("max_workers"), tools.INT)
        assert isinstance(settings.pop("socket_read_timeout"), tools.INT)
        assert not settings

    def test_max_workers(self, childobj):
        """Pass."""
        settings = childobj.max_workers(value=20)
        assert settings["max_workers"] == 20

    def test_socket_read_timeout(self, childobj):
        """Pass."""
        settings = childobj.socket_read_timeout(value=5)
        assert settings["socket_read_timeout"] == 5


class TestSystemInstances(object):
    """Pass."""

    @pytest.fixture(scope="class")
    def childobj(self, apiobj):
        """Pass."""
        return apiobj.instances

    def test_get(self, childobj):
        """Pass."""
        data = childobj.get()
        assert isinstance(data, dict)


class TestSystemRoles(object):
    """Pass."""

    @pytest.fixture(scope="class")
    def childobj(self, apiobj):
        """Pass."""
        return apiobj.roles

    def test__get(self, childobj):
        """Pass."""
        data = childobj._get()
        assert isinstance(data, tools.LIST)
        for x in data:
            assert isinstance(x, dict)

    def test_get_set_default(self, childobj):
        """Pass."""
        roles = childobj.get()
        current_role = childobj.get_default()
        assert isinstance(current_role, dict)

        new_roles = [x for x in roles if x["name"] != current_role["name"]]
        if new_roles:
            new_role = new_roles[0]["name"]
            updated_role = childobj.set_default(new_role)
            assert isinstance(updated_role, dict)
            assert updated_role["name"] == new_role

    def test_add_invalid_perm(self, childobj):
        """Pass."""
        with pytest.raises(exceptions.ApiError):
            childobj.add("x", "badwolf_itai")

    def test_add_get_update_delete(self, childobj):
        """Pass."""
        try:
            childobj.get(name=meta.system.TEST_USER)
        except exceptions.ApiError:
            pass
        else:
            childobj.delete(name=meta.system.TEST_USER)

        added = childobj.add(name=meta.system.TEST_USER)
        assert isinstance(added, dict)
        assert added["name"] == meta.system.TEST_USER
        assert isinstance(added["permissions"], dict)

        with pytest.raises(exceptions.ApiError):
            childobj.add(name=meta.system.TEST_USER)

        added_permissions = added["permissions"]
        update_permissions = {}

        for k, v in added_permissions.items():
            assert v == axonapi.constants.DEFAULT_PERM
            update_permissions[k.lower()] = meta.system.TEST_PERM

        updated = childobj.update(name=meta.system.TEST_USER, **update_permissions)
        assert isinstance(updated, dict)

        updated_permissions = updated["permissions"]
        for k, v in updated_permissions.items():
            assert v == meta.system.TEST_PERM

        deleted = childobj.delete(name=meta.system.TEST_USER)
        assert isinstance(deleted, tools.LIST)
        assert not [x for x in deleted if x["name"] == added["name"]]

        with pytest.raises(exceptions.ApiError):
            childobj.update(name=meta.system.TEST_USER)

        with pytest.raises(exceptions.ApiError):
            childobj.get(name=meta.system.TEST_USER)


class TestSystemUsers(object):
    """Pass."""

    @pytest.fixture(scope="class")
    def childobj(self, apiobj):
        """Pass."""
        return apiobj.users

    def test__get(self, childobj):
        """Pass."""
        data = childobj._get()
        assert isinstance(data, tools.LIST)
        for x in data:
            assert isinstance(x, dict)

    def test__get_limit(self, childobj):
        """Pass."""
        data = childobj._get(limit=1)
        assert isinstance(data, tools.LIST)
        for x in data:
            assert isinstance(x, dict)
        assert len(data) == 1

    def test__get_limit_skip(self, childobj):
        """Pass."""
        all_data = childobj._get()
        data = childobj._get(limit=1, skip=1)
        assert isinstance(data, tools.LIST)
        for x in data:
            assert isinstance(x, dict)
        assert len(data) == len(all_data[:1])

    def test_add_get_update_delete(self, childobj):
        """Pass."""
        try:
            childobj.get(name=meta.system.TEST_USER)
        except exceptions.ApiError:
            pass
        else:
            childobj.delete(name=meta.system.TEST_USER)

        added = childobj.add(name=meta.system.TEST_USER, password=meta.system.TEST_USER)
        assert isinstance(added, dict)
        assert added["user_name"] == meta.system.TEST_USER
        assert not added["first_name"]
        assert not added["last_name"]
        assert added["password"] == ["unchanged"]

        with pytest.raises(exceptions.ApiError):
            childobj.add(name=meta.system.TEST_USER, password=meta.system.TEST_USER)

        updated = childobj.update(
            name=meta.system.TEST_USER,
            firstname=meta.system.TEST_USER,
            lastname=meta.system.TEST_USER,
            password=meta.system.TEST_USER,
        )
        assert isinstance(updated, dict)
        assert updated["user_name"] == meta.system.TEST_USER
        assert updated["first_name"] == meta.system.TEST_USER
        assert updated["last_name"] == meta.system.TEST_USER
        assert updated["password"] == ["unchanged"]

        deleted = childobj.delete(name=meta.system.TEST_USER)
        assert isinstance(deleted, tools.LIST)
        assert not [x for x in deleted if x["uuid"] == added["uuid"]]

        with pytest.raises(exceptions.ApiError):
            childobj.update(name=meta.system.TEST_USER)

        with pytest.raises(exceptions.ApiError):
            childobj.get(name=meta.system.TEST_USER)
