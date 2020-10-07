# -*- coding: utf-8 -*-
"""Test suite."""
import copy
import datetime

import pytest

from axonius_api_client.exceptions import NotFoundError


class TestInstancesPublic:
    @pytest.fixture(scope="class")
    def apiobj(self, api_instances):
        return api_instances

    def test_get(self, apiobj):
        data = apiobj.get()
        assert isinstance(data, dict)

        connection_data = data.pop("connection_data")
        assert isinstance(connection_data, dict)

        instances = data.pop("instances")
        assert isinstance(instances, list) and instances

        for instance in instances:
            val_instance(instance)

        assert not data

    def test_get_collectors(self, apiobj):
        instances = apiobj.get_collectors()
        assert isinstance(instances, list)

        for instance in instances:
            val_instance(instance)

    def test_get_central_core_config(self, apiobj):
        data = apiobj.get_central_core_config()
        bools = ["core_delete_backups", "central_core_enabled"]

        for i in bools:
            v = data.pop(i)
            assert isinstance(v, bool)

        assert not data

    def test_get_set_core_delete_mode(self, apiobj):
        orig_value = apiobj.get_core_delete_mode()
        assert isinstance(orig_value, bool)

        update_value = apiobj.set_core_delete_mode(enabled=not orig_value)
        assert update_value is not orig_value

        reset_value = apiobj.set_core_delete_mode(enabled=orig_value)
        assert reset_value == orig_value

    def test_get_set_central_core_mode(self, apiobj):
        orig_value = apiobj.get_central_core_mode()
        assert isinstance(orig_value, bool)

        update_value = apiobj.set_central_core_mode(enabled=not orig_value)
        assert update_value is not orig_value

        reset_value = apiobj.set_central_core_mode(enabled=orig_value)
        assert reset_value == orig_value

    def test_get_set_is_env_name(self, apiobj):
        node_name = apiobj.get_core(key="node_name")
        orig_value = apiobj.get_is_env_name(name=node_name)
        assert isinstance(orig_value, bool)

        update_value = apiobj.set_is_env_name(name=node_name, enabled=not orig_value)
        assert update_value is not orig_value

        reset_value = apiobj.set_is_env_name(name=node_name, enabled=orig_value)
        assert reset_value == orig_value

    def test_get_set_hostname(self, apiobj):
        node_name = apiobj.get_core(key="node_name")
        orig_value = apiobj.get_hostname(name=node_name)
        assert isinstance(orig_value, str)

        new_value = f"{orig_value}-a"
        update_value = apiobj.set_hostname(name=node_name, value=new_value)
        assert update_value == new_value

        reset_value = apiobj.set_hostname(name=node_name, value=orig_value)
        assert reset_value == orig_value

    def test_feature_flags(self, apiobj):
        value = apiobj.feature_flags
        assert isinstance(value, dict)
        assert isinstance(value["config"], dict)
        assert isinstance(value["schema"], dict)

    def test_has_cloud_compliance(self, apiobj):
        value = apiobj.has_cloud_compliance
        assert isinstance(value, bool)

    def test_license_expiry(self, apiobj):
        value = apiobj.license_expiry
        assert isinstance(value, datetime.datetime) or value is None

    def test_license_days_left(self, apiobj):
        value = apiobj.license_days_left
        assert isinstance(value, int) or value is None

    def test_trial_expiry(self, apiobj):
        value = apiobj.trial_expiry
        assert isinstance(value, datetime.datetime) or value is None

    def test_trial_days_left(self, apiobj):
        value = apiobj.trial_days_left
        assert isinstance(value, int) or value is None

    def test_get_by_name_invalid(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get_by_name("badwolf")

    def test_set_name(self, apiobj):
        orig_value = apiobj.get_core(key="name")
        new_value = "Test"

        update_value = apiobj.set_name(name=orig_value, new_name=new_value)
        assert update_value == new_value

        reset_value = apiobj.set_name(name=new_value, new_name=orig_value)
        assert reset_value == orig_value


class TestInstancesPrivate:
    @pytest.fixture(scope="class")
    def apiobj(self, api_instances):
        return api_instances

    def test_get_update(self, apiobj):
        data = apiobj._get()
        assert isinstance(data, dict)

        connection_data = data.pop("connection_data")
        assert isinstance(connection_data, dict)

        instances = data.pop("instances")
        assert isinstance(instances, list) and instances

        assert not data

        node_id = instances[0]["node_id"]
        node_name = instances[0]["node_name"]
        hostname = instances[0]["hostname"]
        use_env = instances[0]["use_as_environment_name"]

        for instance in instances:
            val_raw_instance(instance)

        update = apiobj._update(
            node_id=node_id,
            node_name=node_name,
            hostname=hostname,
            use_as_environment_name=not use_env,
        )
        assert not update

        reget = apiobj._get()["instances"][0]["use_as_environment_name"]
        assert reget is not use_env

        reset = apiobj._update(
            node_id=node_id,
            node_name=node_name,
            hostname=hostname,
            use_as_environment_name=use_env,
        )
        assert not reset

        reget = apiobj._get()["instances"][0]["use_as_environment_name"]
        assert reget is use_env

    def test_get_update_central_core(self, apiobj):
        orig_value = apiobj._get_central_core()
        current = copy.deepcopy(orig_value)
        current["delete_backups"] = not current["delete_backups"]
        value = apiobj._update_central_core(**current)
        assert value == current

        value["delete_backups"] = not value["delete_backups"]
        value = apiobj._update_central_core(**value)
        assert value == orig_value

    def test_feature_flags(self, apiobj):
        value = apiobj._feature_flags()
        assert isinstance(value, dict)
        assert isinstance(value["config"], dict)
        assert isinstance(value["schema"], dict)


def val_instance(instance):
    val_raw_instance(instance=instance, done=False)
    floats = [
        "data_disk_free_space_gb",
        "data_disk_size_gb",
        "data_disk_free_space_percent",
        "memory_free_space_gb",
        "memory_size_gb",
        "memory_free_space_percent",
        "swap_free_space_gb",
        "swap_size_gb",
        "swap_free_space_percent",
        "os_disk_free_space_gb",
        "os_disk_size_gb",
        "os_disk_free_space_percent",
    ]
    strs = ["name", "id"]

    for i in floats:
        v = instance.pop(i)
        assert isinstance(v, float)

    for i in strs:
        v = instance.pop(i)
        assert isinstance(v, str)

    assert not instance


def val_raw_instance(instance, done=True):
    assert isinstance(instance, dict)
    ints = [
        "cpu_core_threads",
        "cpu_cores",
        "cpu_usage",
        "data_disk_free_space",
        "data_disk_size",
        "last_snapshot_size",
        "max_snapshots",
        "swap_cache_size",
        "swap_free_space",
        "swap_size",
        "os_disk_free_space",
        "os_disk_size",
        "physical_cpu",
    ]

    floats = ["memory_free_space", "memory_size"]

    strs = [
        "hostname",
        "last_seen",
        "last_updated",
        "node_id",
        "node_name",
        "node_user_password",
        "status",
    ]
    bools = ["is_master", "use_as_environment_name"]

    for i in ints:
        v = instance.pop(i)
        assert isinstance(v, int) and (v is not False or v is not True)

    for i in floats:
        v = instance.pop(i)
        assert isinstance(v, float)

    for i in strs:
        v = instance.pop(i)
        assert isinstance(v, str)

    for i in bools:
        v = instance.pop(i)
        assert v is True or v is False

    tags = instance.pop("tags")
    assert isinstance(tags, dict)
    ips = instance.pop("ips")
    assert isinstance(ips, list) and ips
    assert ips[0]

    if done:
        assert not instance
