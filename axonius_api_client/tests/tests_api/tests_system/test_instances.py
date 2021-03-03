# -*- coding: utf-8 -*-
"""Test suite."""
import datetime

import pytest

from axonius_api_client.api import json_api
from axonius_api_client.exceptions import NotFoundError


class TestInstancesPublic:
    @pytest.fixture(scope="class")
    def apiobj(self, api_instances):
        return api_instances

    def test_get(self, apiobj):
        data = apiobj.get()
        assert isinstance(data, list) and data
        for item in data:
            assert isinstance(item, dict)

    def test_get_collectors(self, apiobj):
        instances = apiobj.get_collectors()
        assert isinstance(instances, list)

        for instance in instances:
            assert isinstance(instance, dict)

    def test_get_central_core_config(self, apiobj):
        data = apiobj.get_central_core_config()
        bools = ["delete_backups", "enabled"]

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
        assert isinstance(value, json_api.system_settings.FeatureFlags)
        assert isinstance(value.config, dict)
        assert isinstance(value.document_meta["schema"], dict)

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
        assert isinstance(data, list)
        for item in data:
            assert isinstance(item, json_api.instances.Instance)

        instance = data[0]

        node_id = instance.node_id
        node_name = instance.node_name
        hostname = instance.hostname
        use_env = instance.use_as_environment_name

        update = apiobj._update_attrs(
            node_id=node_id,
            node_name=node_name,
            hostname=hostname,
            use_as_environment_name=not use_env,
        )
        assert not update

        reget = apiobj._get()[0].use_as_environment_name
        assert reget is not use_env

        reset = apiobj._update_attrs(
            node_id=node_id,
            node_name=node_name,
            hostname=hostname,
            use_as_environment_name=use_env,
        )
        assert not reset

        reget = apiobj._get()[0].use_as_environment_name
        assert reget is use_env

    def test_get_update_central_core(self, apiobj):
        settings = apiobj._get_central_core_config()
        assert isinstance(settings, json_api.system_settings.SystemSettings)

        config_key = "delete_backups"
        value_orig = settings.config[config_key]
        value_to_set = not value_orig

        to_update = {}
        to_update.update(settings.config)
        to_update[config_key] = value_to_set
        updated = apiobj._update_central_core_config(**to_update)
        assert isinstance(updated, json_api.system_settings.SystemSettings)
        assert updated.config == to_update

        to_restore = {}
        to_restore.update(settings.config)
        to_restore[config_key] = value_orig

        restored = apiobj._update_central_core_config(**to_restore)
        assert restored.config == settings.config

    def test_feature_flags(self, apiobj):
        value = apiobj._feature_flags()
        assert isinstance(value, json_api.system_settings.FeatureFlags)
        assert isinstance(value.config, dict)
        assert isinstance(value.document_meta["schema"], dict)
