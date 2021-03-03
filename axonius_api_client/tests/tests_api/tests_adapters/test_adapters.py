# -*- coding: utf-8 -*-
"""Test suite."""
import copy

import pytest

from axonius_api_client.api import json_api
from axonius_api_client.constants.adapters import CSV_ADAPTER
from axonius_api_client.exceptions import ApiError, ConfigUnchanged, ConfigUnknown, NotFoundError

from ...meta import CSV_FILECONTENT_BYTES, CSV_FILECONTENT_STR, CSV_FILENAME


class TestAdaptersBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_adapters):
        return api_adapters

    @pytest.fixture(scope="class")
    def adapter(self, apiobj):
        return apiobj.get_by_name(name=CSV_ADAPTER, get_clients=False)


class TestAdaptersPrivate(TestAdaptersBase):
    # TAKES FOREVER
    # def test_private_get(self, apiobj):
    #     adapters = apiobj._get()
    #     assert isinstance(adapters, list) and adapters
    #     for adapter in adapters:
    #         assert isinstance(adapter, json_api.adapters.Adapter)
    #         for adapter_node in adapter.adapter_nodes:
    #             assert isinstance(adapter_node, json_api.adapters.AdapterNode)
    #             an_serial = adapter_node.to_dict_old()
    #             generic = an_serial["schemas"]["generic"]
    #             discovery = an_serial["schemas"]["discovery"]
    #             assert isinstance(generic, dict) and generic
    #             assert isinstance(discovery, dict) and discovery
    #             for adapter_node_cnx in adapter_node.cnxs:
    #                 assert isinstance(adapter_node_cnx, json_api.adapters.AdapterNodeCnx)
    #                 anc_serial = adapter_node_cnx.to_dict_old()
    #                 assert isinstance(anc_serial, dict)

    def test_private_get_no_clients(self, apiobj):
        adapters = apiobj._get(get_clients=False)
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

    def test_private_file_upload_str(self, apiobj, adapter):
        data = apiobj._file_upload(
            adapter_name=adapter["name_raw"],
            node_id=adapter["node_id"],
            field_name=CSV_ADAPTER,
            file_name=CSV_FILENAME,
            file_content=CSV_FILECONTENT_STR,
        )
        assert isinstance(data, dict)
        assert isinstance(data["uuid"], str) and data["uuid"]
        assert isinstance(data["filename"], str) and data["filename"]

    def test_private_file_upload_bytes(self, apiobj, adapter):
        data = apiobj._file_upload(
            adapter_name=adapter["name_raw"],
            node_id=adapter["node_id"],
            field_name=CSV_ADAPTER,
            file_name=CSV_FILENAME,
            file_content=CSV_FILECONTENT_BYTES,
        )
        assert isinstance(data, dict)
        assert isinstance(data["uuid"], str) and data["uuid"]
        assert isinstance(data["filename"], str) and data["filename"]

    def test_private_config_update(self, apiobj, adapter):
        adapter_name_raw = adapter["name_raw"]
        config_key = "user_last_fetched_threshold_hours"

        settings = apiobj._config_get(adapter_name=adapter_name_raw)
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
        update_response = apiobj._config_update(
            adapter_name=adapter_name_raw,
            config_name=settings.schema_name_generic,
            config=generic_update,
        )
        assert isinstance(update_response, json_api.system_settings.SystemSettings)
        assert update_response.config[config_key] == value_to_set

        reset_response = apiobj._config_update(
            adapter_name=adapter_name_raw,
            config_name=settings.schema_name_generic,
            config=generic,
        )
        assert isinstance(reset_response, json_api.system_settings.SystemSettings)
        assert reset_response.config[config_key] == generic[config_key]


class TestAdaptersPublic(TestAdaptersBase):
    def test_get(self, apiobj):
        adapters = apiobj.get(get_clients=False)
        assert all(["schemas" in x for x in adapters])

    def test_get_by_name(self, apiobj):
        adapter = apiobj.get_by_name(name=CSV_ADAPTER, get_clients=False)
        assert "schemas" in adapter

    def test_get_by_name_bad_node(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get_by_name(name=CSV_ADAPTER, node="badwolf", get_clients=False)

    def test_get_by_name_bad_name(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.get_by_name(name="badwolf", get_clients=False)

    def test_config_get_bad_config_type(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.config_get(name=CSV_ADAPTER, config_type="badwolf")

    def test_config_get_discovery(self, apiobj):
        data = apiobj.config_get(name="aws", config_type="discovery")
        assert isinstance(data, dict)
        config = data.pop("config")
        assert isinstance(config, dict) and config

        schema = data.pop("schema")
        assert isinstance(schema, dict) and schema

    def test_config_get_specific(self, apiobj):
        data = apiobj.config_get(name="aws", config_type="specific")
        assert isinstance(data, dict)
        config = data.pop("config")
        assert isinstance(config, dict) and config

        schema = data.pop("schema")
        assert isinstance(schema, dict) and schema

    def test_config_get_generic(self, apiobj):
        data = apiobj.config_get(name=CSV_ADAPTER, config_type="generic")
        assert isinstance(data, dict)

        config = data.pop("config")
        assert isinstance(config, dict) and config

        schema = data.pop("schema")
        assert isinstance(schema, dict) and schema

    def test_file_upload_str(self, apiobj, adapter):
        data = apiobj.file_upload(
            name=adapter["name"],
            node=adapter["node_name"],
            field_name=CSV_ADAPTER,
            file_name=CSV_FILENAME,
            file_content=CSV_FILECONTENT_STR,
        )
        assert isinstance(data, dict)
        assert data["uuid"]
        assert data["filename"]

    def test_file_upload_path(self, apiobj, tmp_path):
        test_path = tmp_path / CSV_FILENAME
        test_path.write_text(CSV_FILECONTENT_STR)

        data = apiobj.file_upload_path(
            name=CSV_ADAPTER,
            path=test_path,
        )
        assert isinstance(data, dict)
        assert data["uuid"]
        assert data["filename"]

    def test_config_update_unknown(self, apiobj):
        with pytest.raises(ConfigUnknown):
            apiobj.config_update(
                name=CSV_ADAPTER,
                config_type="generic",
                badwolf="badwolf",
            )

    def test_config_update_unchanged(self, apiobj):
        with pytest.raises(ConfigUnchanged):
            apiobj.config_update(name=CSV_ADAPTER, config_type="generic")

    def test_config_update_generic(self, apiobj, adapter):
        data = apiobj.config_get(name=adapter["name"])
        current = data["config"]
        key = "user_last_fetched_threshold_hours"
        current_value = current[key]
        new_value = current_value + 1

        set_response = apiobj.config_update(
            name=adapter["name"],
            node=adapter["node_name"],
            user_last_fetched_threshold_hours=new_value,
            config_type="generic",
        )
        set_value = set_response["config"][key]
        assert set_value == new_value

        reset_response = apiobj.config_update(
            name=adapter["name"],
            node=adapter["node_name"],
            user_last_fetched_threshold_hours=current_value,
            config_type="generic",
        )
        reset_value = reset_response["config"][key]
        assert reset_value == current_value
