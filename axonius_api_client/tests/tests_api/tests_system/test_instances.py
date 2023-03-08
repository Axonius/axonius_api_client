# -*- coding: utf-8 -*-
"""Test suite."""
import datetime

import pytest

from axonius_api_client.api import Instances, json_api
from axonius_api_client.api.api_endpoints import ApiEndpoints
from axonius_api_client.exceptions import FeatureNotEnabledError, NotFoundError


class InstancesBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_instances):
        return api_instances


class TestInstancesPublic(InstancesBase):
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

        # new in 4.5, gone in 4.7
        # now_offset = data.pop("now_offset")
        # assert isinstance(now_offset, int)

        # assert not data

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
        assert isinstance(value.data_scopes_max, (int, type(None)))

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

    def test_admin_script_upload_path_file(self, apiobj, tmp_path):
        file_path = tmp_path / "admin_script_test.txt"
        file_path.write_text("badwolf\nbadwolf\nbadwolf")
        data = apiobj.admin_script_upload_path(path=file_path)
        assert isinstance(data, dict) and data
        assert data["file_name"] == "admin_script_test.txt"
        assert isinstance(data["file_uuid"], str) and data["file_uuid"]
        assert data["execute_result"] == "file executed"

    def test_admin_script_upload_path_url(self, apiobj):
        path = f"{apiobj.http.url}/{ApiEndpoints.system_settings.meta_about.path}"
        data = apiobj.admin_script_upload_path(path=path, path_verify=False)
        assert isinstance(data, dict) and data
        assert data["file_name"] == "about"
        assert isinstance(data["file_uuid"], str) and data["file_uuid"]
        assert data["execute_result"] == "file executed"


class TestInstancesPrivate(InstancesBase):
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
        original = apiobj._get_central_core_config()
        assert isinstance(original, json_api.system_settings.SystemSettings)

        value_original = original.config["delete_backups"]
        value_to_set = not value_original

        updated = apiobj._update_central_core_config(
            delete_backups=value_to_set, enabled=original.config["enabled"]
        )
        assert isinstance(updated, json_api.system_settings.SystemSettings)
        assert updated.config["delete_backups"] == value_to_set
        assert updated.config["enabled"] == original.config["enabled"]

        restored = apiobj._update_central_core_config(
            delete_backups=value_original, enabled=original.config["enabled"]
        )
        assert restored.config["delete_backups"] == value_original
        assert restored.config["enabled"] == original.config["enabled"]

    def test_feature_flags(self, apiobj):
        value = apiobj._feature_flags()
        assert isinstance(value, json_api.system_settings.FeatureFlags)
        assert isinstance(value.config, dict)
        assert isinstance(value.document_meta["schema"], dict)


@pytest.mark.tunneltests
class TestInstancesTunnels(InstancesBase):
    def test_check_tunnel_feature_error_false(self, apiobj):
        enabled = apiobj.has_saas_enabled
        ret = apiobj.check_tunnel_feature(feature_error=False)
        assert ret == enabled

    def test_check_tunnel_feature_disabled_error_true(self, apiobj, monkeypatch):
        monkeypatch.setattr(Instances, "has_saas_enabled", False)

        with pytest.raises(FeatureNotEnabledError):
            apiobj.check_tunnel_feature(feature_error=True)

    def test_check_tunnel_feature_enabled_error_true(self, apiobj, monkeypatch):
        monkeypatch.setattr(Instances, "has_saas_enabled", True)
        ret = apiobj.check_tunnel_feature(feature_error=True)
        assert ret is True

    def test_get_tunnels(self, apiobj, tunnel_feature_check):
        data = apiobj.get_tunnels()
        assert isinstance(data, list)
        for item in data:
            assert isinstance(item, json_api.instances.Tunnel)

    def test_get_tunnel_default(self, apiobj, tunnel_count_check):
        data = apiobj.get_tunnel_default()
        assert isinstance(data, json_api.instances.Tunnel)

    def test_get_tunnel_invalid(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get_tunnel(value="xxx", feature_error=False)
