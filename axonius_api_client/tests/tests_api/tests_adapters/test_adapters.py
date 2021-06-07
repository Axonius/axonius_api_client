# -*- coding: utf-8 -*-
"""Test suite."""
import copy

import pytest
from axonius_api_client.api import ApiEndpoints, json_api
from axonius_api_client.constants.adapters import CSV_ADAPTER
from axonius_api_client.exceptions import (ApiError, ConfigUnchanged,
                                           ConfigUnknown, NotFoundError)

from ...meta import CSV_FILECONTENT_BYTES, CSV_FILECONTENT_STR, CSV_FILENAME
from ...utils import cross_check_endpoint_models, get_cnx_existing


class TestAdaptersBase:
    @pytest.fixture(scope="class")
    def adapter(self, api_client):
        return api_client.adapters.get_by_name(name=CSV_ADAPTER, get_clients=False)


class TestAdaptersPrivate(TestAdaptersBase):
    @pytest.mark.parametrize(
        "name,endpoint", [[k, v] for k, v in ApiEndpoints.adapters.get_fields_dict().items()]
    )
    def test_json_api_models_request(self, name, endpoint):
        cross_check_endpoint_models(
            name=name,
            endpoint=endpoint,
            schema_model=endpoint.request_schema_cls,
            data_model=endpoint.request_model_cls,
        )

    @pytest.mark.parametrize(
        "name,endpoint", [[k, v] for k, v in ApiEndpoints.adapters.get_fields_dict().items()]
    )
    def test_json_api_models_response(self, name, endpoint):
        cross_check_endpoint_models(
            name=name,
            endpoint=endpoint,
            schema_model=endpoint.response_schema_cls,
            data_model=endpoint.response_model_cls,
        )

    def test_private_get_clients_true(self, api_client):
        # with get_clients=True, this can take an eternity
        # possibly due to cache resets post connection update/delete

        adapters = api_client.adapters._get(get_clients=True)
        assert isinstance(adapters, list) and adapters
        for adapter in adapters:
            assert isinstance(adapter, json_api.adapters.Adapter)
            assert adapter.adapter_name in str(adapter)
            for adapter_node in adapter.adapter_nodes:
                assert isinstance(adapter_node, json_api.adapters.AdapterNode)
                assert adapter.adapter_name in str(adapter_node)

                serial = adapter_node.to_dict_old()
                generic = serial["schemas"]["generic"]
                discovery = serial["schemas"]["discovery"]
                assert isinstance(generic, dict) and generic
                assert isinstance(discovery, dict) and discovery
                for cnx in adapter_node.cnxs:
                    assert isinstance(cnx, json_api.adapters.AdapterNodeCnx)
                    assert isinstance(cnx.label, str)
                    assert isinstance(cnx.schema_cnx, dict) and cnx.schema_cnx
                    assert isinstance(cnx.schema_cnx_discovery, dict) and cnx.schema_cnx_discovery

    def test_private_get_clients_false(self, api_client):
        adapters = api_client.adapters._get(get_clients=False)
        assert isinstance(adapters, list) and adapters
        for adapter in adapters:
            assert isinstance(adapter, json_api.adapters.Adapter)
            for adapter_node in adapter.adapter_nodes:
                assert isinstance(adapter_node, json_api.adapters.AdapterNode)
                serial = adapter_node.to_dict_old()
                generic = serial["schemas"]["generic"]
                discovery = serial["schemas"]["discovery"]
                assert isinstance(generic, dict) and not generic
                assert isinstance(discovery, dict) and not discovery
                assert not adapter_node.cnxs

    def test_private_file_upload_str(self, api_client, adapter):
        data = api_client.adapters._file_upload(
            adapter_name=adapter["name_raw"],
            node_id=adapter["node_id"],
            field_name=CSV_ADAPTER,
            file_name=CSV_FILENAME,
            file_content=CSV_FILECONTENT_STR,
        )
        assert isinstance(data, dict)
        assert isinstance(data["uuid"], str) and data["uuid"]
        assert isinstance(data["filename"], str) and data["filename"]

    def test_private_file_upload_bytes(self, api_client, adapter):
        data = api_client.adapters._file_upload(
            adapter_name=adapter["name_raw"],
            node_id=adapter["node_id"],
            field_name=CSV_ADAPTER,
            file_name=CSV_FILENAME,
            file_content=CSV_FILECONTENT_BYTES,
        )
        assert isinstance(data, dict)
        assert isinstance(data["uuid"], str) and data["uuid"]
        assert isinstance(data["filename"], str) and data["filename"]

    def test_private_config_update(self, api_client, adapter):
        adapter_name_raw = adapter["name_raw"]
        config_key = "user_last_fetched_threshold_hours"

        settings = api_client.adapters._config_get(adapter_name=adapter_name_raw)
        assert isinstance(settings, json_api.adapters.AdapterSettings)

        generic = settings.config_generic
        assert isinstance(generic, dict) and generic

        generic_update = copy.deepcopy(generic)
        value_to_set = generic_update[config_key]

        if isinstance(value_to_set, int):
            value_to_set += 1
        else:
            value_to_set = 48

        generic_update[config_key] = value_to_set
        update_response = api_client.adapters._config_update(
            adapter_name=adapter_name_raw,
            config_name=settings.schema_name_generic,
            config=generic_update,
        )
        assert isinstance(update_response, json_api.system_settings.SystemSettings)
        assert update_response.config[config_key] == value_to_set

        reset_response = api_client.adapters._config_update(
            adapter_name=adapter_name_raw,
            config_name=settings.schema_name_generic,
            config=generic,
        )
        assert isinstance(reset_response, json_api.system_settings.SystemSettings)
        assert reset_response.config[config_key] == generic[config_key]

    def test_get_basic(self, api_client):
        data = api_client.adapters._get_basic()
        assert isinstance(data, json_api.generic.Metadata)
        assert isinstance(data.adapters, dict)
        for k, v in data.adapters.items():
            assert isinstance(v, dict)
            assert isinstance(v["title"], str)
            assert isinstance(v["name_raw"], str)
            assert isinstance(v["name"], str)
            assert v["name"] == k
            assert data.find_by_name(value=k) == v

        with pytest.raises(NotFoundError):
            data.find_by_name(value="badwolf")

    def test_get_labels(self, api_client, new_csv_cnx):
        data = api_client.adapters._get_labels()
        assert isinstance(data, json_api.adapters.CnxLabels)
        assert data._get_schema_cls() == json_api.adapters.CnxLabelsSchema

        cnx_label = new_csv_cnx["connection_label"]
        cnx_node_id = new_csv_cnx["node_id"]
        cnx_plugin_name = new_csv_cnx["adapter_name_raw"]

        assert cnx_label in data.label_values

        label_keys = ["client_id", "label", "node_id", "plugin_name", "plugin_unique_name"]
        found = False

        for label in data.labels:
            assert sorted(list(label)) == sorted(label_keys)
            label_name = label["label"]
            label_node_id = label["node_id"]
            label_plugin_name = label["plugin_name"]

            if label_name == cnx_label:
                found = True
                assert label_node_id == cnx_node_id
                assert label_plugin_name == cnx_plugin_name

        if not found:
            raise Exception(f"Did not find label {cnx_label}")


class TestAdaptersPublic(TestAdaptersBase):
    def test_get(self, api_client):
        adapters = api_client.adapters.get(get_clients=False)
        assert all(["schemas" in x for x in adapters])

    def test_get_by_name(self, api_client):
        adapter = api_client.adapters.get_by_name(name=CSV_ADAPTER, get_clients=False)
        assert "schemas" in adapter

    def test_get_by_name_bad_node(self, api_client):
        with pytest.raises(NotFoundError):
            api_client.adapters.get_by_name(name=CSV_ADAPTER, node="badwolf", get_clients=False)

    def test_get_by_name_bad_name(self, api_client):
        with pytest.raises(NotFoundError):
            api_client.adapters.get_by_name(name="badwolf", get_clients=False)

    def test_config_get_bad_config_type(self, api_client):
        with pytest.raises(ApiError):
            api_client.adapters.config_get(name=CSV_ADAPTER, config_type="badwolf")

    def test_config_get_discovery(self, api_client):
        data = api_client.adapters.config_get(name="aws", config_type="discovery")
        assert isinstance(data, dict)
        config = data.pop("config")
        assert isinstance(config, dict) and config

        schema = data.pop("schema")
        assert isinstance(schema, dict) and schema

    def test_config_get_specific(self, api_client):
        data = api_client.adapters.config_get(name="aws", config_type="specific")
        assert isinstance(data, dict)
        config = data.pop("config")
        assert isinstance(config, dict) and config

        schema = data.pop("schema")
        assert isinstance(schema, dict) and schema

    def test_config_get_generic(self, api_client):
        data = api_client.adapters.config_get(name=CSV_ADAPTER, config_type="generic")
        assert isinstance(data, dict)

        config = data.pop("config")
        assert isinstance(config, dict) and config

        schema = data.pop("schema")
        assert isinstance(schema, dict) and schema

    def test_file_upload_str(self, api_client, adapter):
        data = api_client.adapters.file_upload(
            name=adapter["name"],
            node=adapter["node_name"],
            field_name=CSV_ADAPTER,
            file_name=CSV_FILENAME,
            file_content=CSV_FILECONTENT_STR,
        )
        assert isinstance(data, dict)
        assert data["uuid"]
        assert data["filename"]

    def test_file_upload_path(self, api_client, tmp_path):
        test_path = tmp_path / CSV_FILENAME
        test_path.write_text(CSV_FILECONTENT_STR)

        data = api_client.adapters.file_upload_path(
            name=CSV_ADAPTER,
            path=test_path,
        )
        assert isinstance(data, dict)
        assert data["uuid"]
        assert data["filename"]

    def test_config_update_unknown(self, api_client):
        with pytest.raises(ConfigUnknown):
            api_client.adapters.config_update(
                name=CSV_ADAPTER,
                config_type="generic",
                badwolf="badwolf",
            )

    def test_config_update_unchanged(self, api_client):
        with pytest.raises(ConfigUnchanged):
            api_client.adapters.config_update(name=CSV_ADAPTER, config_type="generic")

    def test_config_update_generic(self, api_client, adapter):
        data = api_client.adapters.config_get(name=adapter["name"])
        current = data["config"]
        key = "user_last_fetched_threshold_hours"
        current_value = current[key]
        new_value = current_value + 1

        set_response = api_client.adapters.config_update(
            name=adapter["name"],
            node=adapter["node_name"],
            user_last_fetched_threshold_hours=new_value,
            config_type="generic",
        )
        set_value = set_response["config"][key]
        assert set_value == new_value

        reset_response = api_client.adapters.config_update(
            name=adapter["name"],
            node=adapter["node_name"],
            user_last_fetched_threshold_hours=current_value,
            config_type="generic",
        )
        reset_value = reset_response["config"][key]
        assert reset_value == current_value

    def test_get_by_name_basic(self, api_client):
        cnx = get_cnx_existing(api_client)
        data = api_client.adapters.get_by_name_basic(value=cnx["adapter_name"])
        assert isinstance(data, dict)
