# -*- coding: utf-8 -*-
"""Test suite."""
import copy
import warnings

import pytest

from axonius_api_client.constants import CSV_ADAPTER, DEFAULT_NODE
from axonius_api_client.exceptions import (
    ApiError,
    ConfigUnchanged,
    ConfigUnknown,
    NotFoundError,
)

from ...meta import (
    CSV_FILECONTENT_BYTES,
    CSV_FILECONTENT_STR,
    CSV_FILENAME,
    FIELD_FORMATS,
    NO_TITLES,
    SCHEMA_TYPES,
)


def val_parsed_schema(schema):
    """Pass."""
    for setting_name, item in schema.items():
        item_name = item.pop("name")
        assert isinstance(item_name, str) and item_name
        assert setting_name == item_name

        item_type = item.pop("type")
        assert isinstance(item_type, str) and item_type
        assert item_type in SCHEMA_TYPES

        item_required = item.pop("required")
        assert isinstance(item_required, bool)

        item_title = item.pop("title")
        assert isinstance(item_title, str) and item_title

        # optionals
        item_format = item.pop("format", "")
        assert isinstance(item_format, str)
        assert item_format in FIELD_FORMATS or item_format == ""

        item_description = item.pop("description", "")
        assert isinstance(item_description, str)

        item_enum = item.pop("enum", [])
        assert isinstance(item_enum, list)
        for x in item_enum:
            if isinstance(x, dict):
                assert isinstance(x["name"], str)
                assert isinstance(x["title"], str)
                continue
            assert isinstance(x, str) and x

        item_default = item.pop("default", "")
        assert isinstance(item_default, (str, int, bool)) or item_default in [
            None,
            [],
        ]

        item_items = item.pop("items", {})
        if isinstance(item_items, list):
            for x in item_items:
                assert isinstance(x, dict)
                assert isinstance(x["name"], str)
                if x["name"] not in NO_TITLES:
                    assert isinstance(x["title"], str)
                assert isinstance(x["type"], str)
        else:
            assert isinstance(item_items, dict)

        item_report_id = item.pop("report_id", "")
        assert isinstance(item_report_id, str)

        assert not item


class TestAdaptersBase:
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_adapters):
        """Pass."""
        return api_adapters

    @pytest.fixture(scope="class")
    def adapter(self, apiobj):
        """Pass."""
        return apiobj.get_by_name(name=CSV_ADAPTER, node=DEFAULT_NODE)


class TestAdaptersPrivate(TestAdaptersBase):
    """Pass."""

    def test_private_get(self, apiobj):
        """Pass."""
        adapters = apiobj._get()
        assert isinstance(adapters, dict)
        self.val_raw_adapters(adapters=adapters)

    def val_raw_adapters(self, adapters):
        """Pass."""
        for name, instances in adapters.items():
            assert name.endswith("_adapter")
            assert isinstance(instances, list)

            for instance in instances:
                self.val_raw_adapter(name=name, instance=instance)

    def val_raw_adapter(self, name, instance):
        """Pass."""
        node_id = instance.pop("node_id")
        assert isinstance(node_id, str) and node_id

        unique_plugin_name = instance.pop("unique_plugin_name")
        assert isinstance(unique_plugin_name, str) and unique_plugin_name

        node_name = instance.pop("node_name")
        assert isinstance(node_name, str) and node_name

        clients = instance.pop("clients")
        assert isinstance(clients, list)

        config = instance.pop("config")
        assert isinstance(config, dict) and config
        assert len(config) in [2, 3]
        assert "AdapterBase" in config

        for config_name, item in config.items():
            item_config = item.pop("config")
            item_schema = item.pop("schema")
            item_pretty_name = item_schema.pop("pretty_name")

            assert isinstance(item_config, dict) and item_config
            assert isinstance(item_pretty_name, str) and item_pretty_name
            assert isinstance(item_schema, dict) and item_schema

            self.val_raw_schema(name=name, schema=item_schema)

            assert not item

        schema = instance.pop("schema")
        assert isinstance(schema, dict) and schema
        self.val_raw_schema(name=name, schema=schema)

        status = instance.pop("status")
        assert status in ["warning", "success", None, ""]

        supported_features = instance.pop("supported_features")
        assert isinstance(supported_features, list)
        for x in supported_features:
            assert isinstance(x, str)

        assert not instance

        for client in clients:
            self.val_raw_client(name=name, client=client, instance_status=status)

    def val_raw_client(self, name, client, instance_status):
        """Pass."""
        assert isinstance(client, dict)

        client_config = client.pop("client_config")
        assert isinstance(client_config, dict) and client_config

        uuid = client.pop("uuid")
        assert isinstance(uuid, str) and uuid

        client_id = client.pop("client_id")
        assert isinstance(client_id, str)

        if not client_id:
            msg = "Client for {} has an empty client_id {}"
            msg = msg.format(name, client_id)
            warnings.warn(msg)

        error = client.pop("error")
        assert isinstance(error, str) or error is None

        node_id = client.pop("node_id")
        assert isinstance(node_id, str) and node_id

        status = client.pop("status")
        assert isinstance(status, str)
        assert status in ["warning", "error", "success"]

        if status == "error":
            assert instance_status == "warning"

        date_fetched = client.pop("date_fetched")
        assert isinstance(date_fetched, str)

        adapter_name = client.pop("adapter_name")
        assert isinstance(adapter_name, str)

        # TBD: bust out dict?
        connection_discovery = client.pop("connection_discovery")
        assert isinstance(connection_discovery, dict)

        last_fetch_time = client.pop("last_fetch_time")
        assert last_fetch_time is None or isinstance(last_fetch_time, str)

        assert not client

    def val_raw_schema(self, name, schema):
        """Pass."""
        assert isinstance(schema, dict)

        items = schema.pop("items")
        assert isinstance(items, list) and items

        item_names = [x["name"] for x in items]

        for item in items:
            assert isinstance(item, dict)

            item_name = item.pop("name")
            assert isinstance(item_name, str) and item_name

            item_type = item.pop("type")
            assert isinstance(item_type, str) and item_type

            item_title = item.pop("title")
            assert isinstance(item_title, str) and item_title

            item_format = item.pop("format", "")
            assert isinstance(item_format, str)

            item_description = item.pop("description", "")
            assert isinstance(item_description, str)

            item_enum = item.pop("enum", [])
            assert isinstance(item_enum, list)
            for x in item_enum:
                if isinstance(x, dict):
                    assert isinstance(x["name"], str)
                    assert isinstance(x["title"], str)
                    continue
                assert isinstance(x, (str, int))

            item_default = item.pop("default", "")
            assert isinstance(item_default, (str, int, bool)) or item_default is None

            item_items = item.pop("items", {})
            if isinstance(item_items, list):
                for x in item_items:
                    assert isinstance(x, dict)
                    assert isinstance(x["name"], str)
                    if x["name"] not in NO_TITLES:
                        assert isinstance(x["title"], str)
                    assert isinstance(x["type"], str)
                continue
            assert isinstance(item_items, dict)

            item_req = item.pop("required", False)
            assert isinstance(item_req, bool)
            if item_type not in SCHEMA_TYPES:
                msg = "Setting for adapter {!r} has an unexpected item_type {!r}"
                msg = msg.format(name, item_type)
                warnings.warn(msg)

            item_report_id = item.pop("report_id", "")
            assert isinstance(item_report_id, str)

            assert not item

        required = schema.pop("required")
        assert isinstance(required, list)
        for req in required:
            assert isinstance(req, str)

            if req not in item_names:
                msg = "Schema for {} has required item {!r} not in defined items {}"
                msg = msg.format(name, req, item_names)
                warnings.warn(msg)

        schema_type = schema.pop("type")
        assert schema_type == "array"

        assert not schema

    def test_private_file_upload_str(self, apiobj, adapter):
        """Pass."""
        data = apiobj._file_upload(
            name_raw=adapter["name_raw"],
            node_id=adapter["node_id"],
            field_name=CSV_ADAPTER,
            file_name=CSV_FILENAME,
            file_content=CSV_FILECONTENT_STR,
        )
        assert isinstance(data, dict)
        assert data["uuid"]
        assert data["filename"]

    def test_private_file_upload_bytes(self, apiobj, adapter):
        """Pass."""
        data = apiobj._file_upload(
            name_raw=adapter["name_raw"],
            node_id=adapter["node_id"],
            field_name=CSV_ADAPTER,
            file_name=CSV_FILENAME,
            file_content=CSV_FILECONTENT_BYTES,
        )
        assert isinstance(data, dict)
        assert data["uuid"]
        assert data["filename"]

    def test_private_config_update(self, apiobj, adapter):
        """Pass."""
        current = apiobj._config_get(
            name_plugin=adapter["name_plugin"], name_config="AdapterBase"
        )
        key = "user_last_fetched_threshold_hours"
        current_config = current["config"]
        config_update = copy.deepcopy(current_config)
        set_value = config_update[key] + 1
        config_update[key] = set_value

        set_response = apiobj._config_update(
            name_raw=adapter["name_raw"],
            name_config="AdapterBase",
            new_config=config_update,
        )

        assert not set_response
        updated = apiobj._config_get(
            name_plugin=adapter["name_plugin"], name_config="AdapterBase"
        )
        updated_config = updated["config"]
        assert updated_config[key] == set_value
        assert updated_config == config_update
        assert updated_config != current_config

        reconfig_update = copy.deepcopy(updated_config)
        reconfig_update[key] = current_config[key]
        reset_response = apiobj._config_update(
            name_raw=adapter["name_raw"],
            name_config="AdapterBase",
            new_config=reconfig_update,
        )
        assert not reset_response
        post_reset = apiobj._config_get(
            name_plugin=adapter["name_plugin"], name_config="AdapterBase"
        )
        assert post_reset["config"] == current_config

    def test_private_config_get_generic(self, apiobj):
        """Pass."""
        for meta in apiobj.get():
            data = apiobj._config_get(
                name_plugin=meta["name_plugin"],
                name_config=meta["schemas"]["generic_name"],
            )
            assert isinstance(data, dict)

            config = data.pop("config")
            assert isinstance(config, dict)

            schema = data.pop("schema")
            assert isinstance(schema, dict)
            # XXX test schema!

            assert not data

            items = schema.pop("items")
            assert isinstance(items, list)

            pretty_name = schema.pop("pretty_name")
            assert isinstance(pretty_name, str) and pretty_name

            required = schema.pop("required")
            assert isinstance(required, list)
            assert all([isinstance(x, str) for x in required])

            stype = schema.pop("type")
            assert stype == "array"

            assert not schema

    def test_private_config_get_specific(self, apiobj):
        """Pass."""
        for meta in apiobj.get():
            if not meta["schemas"]["specific_name"]:
                continue

            data = apiobj._config_get(
                name_plugin=meta["name_plugin"],
                name_config=meta["schemas"]["specific_name"],
            )
            assert isinstance(data, dict)

            config = data.pop("config")
            assert isinstance(config, dict)

            schema = data.pop("schema")
            assert isinstance(schema, dict)

            assert not data

            items = schema.pop("items")
            assert isinstance(items, list)

            pretty_name = schema.pop("pretty_name")
            assert isinstance(pretty_name, str) and pretty_name

            required = schema.pop("required")
            assert isinstance(required, list)
            assert all([isinstance(x, str) for x in required])

            stype = schema.pop("type")
            assert stype == "array"

            assert not schema


class TestAdaptersPublic(TestAdaptersBase):
    """Pass."""

    def test_get(self, apiobj):
        """Pass."""
        adapters = apiobj.get()
        assert all(["schemas" in x for x in adapters])
        self.val_parsed_adapters(adapters=adapters)

    def val_parsed_adapters(self, adapters):
        """Pass."""
        assert isinstance(adapters, list)
        for adapter in adapters:
            self.val_parsed_adapter(adapter=adapter)

    def val_parsed_adapter(self, adapter):
        """Pass."""
        assert isinstance(adapter, dict)

        name = adapter.pop("name")
        assert isinstance(name, str)

        name_raw = adapter.pop("name_raw")
        assert isinstance(name_raw, str)

        name_plugin = adapter.pop("name_plugin")
        assert isinstance(name_plugin, str)

        node_name = adapter.pop("node_name")
        assert isinstance(node_name, str)

        node_id = adapter.pop("node_id")
        assert isinstance(node_id, str)

        status = adapter.pop("status")
        assert isinstance(status, str)
        assert status in ["warning", "success", ""]

        features = adapter.pop("features")
        assert isinstance(features, list)
        for x in features:
            assert isinstance(x, str) and x

        schemas = adapter.pop("schemas")
        assert isinstance(schemas, dict) and schemas

        schema_cnx = schemas.pop("cnx")
        assert isinstance(schema_cnx, dict) and schema_cnx

        generic_name = schemas.pop("generic_name")
        assert isinstance(generic_name, str) and generic_name
        assert generic_name == "AdapterBase"

        generic_schema = schemas.pop("generic")
        assert isinstance(generic_schema, dict) and generic_schema
        val_parsed_schema(schema=generic_schema)

        specific_name = schemas.pop("specific_name")
        assert isinstance(specific_name, str)

        specific_schema = schemas.pop("specific")
        assert isinstance(specific_schema, dict)

        discovery_name = schemas.pop("discovery_name")
        assert isinstance(discovery_name, str)

        discovery_schema = schemas.pop("discovery")
        val_parsed_schema(schema=discovery_schema)

        assert not schemas

        if specific_name:
            assert specific_schema
            val_parsed_schema(schema=specific_schema)

        cnx_count_total = adapter.pop("cnx_count_total")
        assert isinstance(cnx_count_total, int)
        if not cnx_count_total:
            assert not status

        cnx_count_broken = adapter.pop("cnx_count_broken")
        assert isinstance(cnx_count_broken, int)

        cnx_count_working = adapter.pop("cnx_count_working")
        assert isinstance(cnx_count_working, int)
        if not cnx_count_broken and cnx_count_working:
            assert status == "success"

        cnxs = adapter.pop("cnx")
        assert isinstance(cnxs, list)
        for cnx in cnxs:
            self.val_parsed_cnx(
                cnx=cnx,
                adapter_name=name,
                adapter_name_raw=name_raw,
                adapter_node_id=node_id,
                adapter_node_name=node_name,
            )

        config = adapter.pop("config")
        assert isinstance(config, dict) and config

        generic_config = config.pop("generic")
        assert isinstance(generic_config, dict) and generic_config

        specific_config = config.pop("specific")
        assert isinstance(specific_config, dict)

        assert not adapter

    def val_parsed_cnx(
        self, cnx, adapter_name, adapter_name_raw, adapter_node_id, adapter_node_name,
    ):
        """Pass."""
        assert isinstance(cnx, dict)

        cnx_adapter_name = cnx.pop("adapter_name")
        assert cnx_adapter_name == adapter_name

        cnx_adapter_name_raw = cnx.pop("adapter_name_raw")
        assert cnx_adapter_name_raw == adapter_name_raw

        config = cnx.pop("config")
        assert isinstance(config, dict) and config

        date_fetched = cnx.pop("date_fetched")
        assert isinstance(date_fetched, str)

        error = cnx.pop("error")
        assert isinstance(error, str) or error is None

        cnx_id = cnx.pop("id")
        assert isinstance(cnx_id, str)

        cnx_node_id = cnx.pop("node_id")
        assert cnx_node_id == adapter_node_id

        cnx_node_name = cnx.pop("node_name")
        assert cnx_node_name == adapter_node_name

        working = cnx.pop("working")
        assert isinstance(working, bool)

        status = cnx.pop("status")
        assert isinstance(status, str) and status
        assert status in ["warning", "error", "success"]

        uuid = cnx.pop("uuid")
        assert isinstance(uuid, str) and uuid

        assert not cnx

    def test_get_by_name(self, apiobj):
        """Pass."""
        adapter = apiobj.get_by_name(name=CSV_ADAPTER, node=DEFAULT_NODE)
        assert "schemas" in adapter
        self.val_parsed_adapter(adapter=adapter)

    def test_get_by_name_bad_node(self, apiobj):
        """Pass."""
        with pytest.raises(NotFoundError):
            apiobj.get_by_name(name=CSV_ADAPTER, node="badwolf")

    def test_get_by_name_bad_name(self, apiobj):
        """Pass."""
        with pytest.raises(NotFoundError):
            apiobj.get_by_name(name="badwolf", node=DEFAULT_NODE)

    def test_config_get_bad_config_type(self, apiobj):
        """Pass."""
        with pytest.raises(ApiError):
            apiobj.config_get(name=CSV_ADAPTER, node=DEFAULT_NODE, config_type="badwolf")

    def test_config_get_specific(self, apiobj):
        """Pass."""
        data = apiobj.config_get(name="aws", node=DEFAULT_NODE, config_type="specific")
        assert isinstance(data, dict)
        config = data.pop("config")
        assert isinstance(config, dict) and config

        schema = data.pop("schema")
        assert isinstance(schema, dict) and schema

        val_parsed_schema(schema=schema)

    def test_config_get_generic(self, apiobj):
        """Pass."""
        data = apiobj.config_get(
            name=CSV_ADAPTER, node=DEFAULT_NODE, config_type="generic"
        )
        assert isinstance(data, dict)

        config = data.pop("config")
        assert isinstance(config, dict) and config

        schema = data.pop("schema")
        assert isinstance(schema, dict) and schema

        val_parsed_schema(schema=schema)

    def test_file_upload_str(self, apiobj, adapter):
        """Pass."""
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
        """Pass."""
        test_path = tmp_path / CSV_FILENAME
        test_path.write_text(CSV_FILECONTENT_STR)

        data = apiobj.file_upload_path(
            name=CSV_ADAPTER, node=DEFAULT_NODE, path=test_path,
        )
        assert isinstance(data, dict)
        assert data["uuid"]
        assert data["filename"]

    def test_config_update_unknown(self, apiobj):
        """Pass."""
        with pytest.raises(ConfigUnknown):
            apiobj.config_update(
                name=CSV_ADAPTER,
                node=DEFAULT_NODE,
                config_type="generic",
                badwolf="badwolf",
            )

    def test_config_update_unchanged(self, apiobj):
        """Pass."""
        with pytest.raises(ConfigUnchanged):
            apiobj.config_update(
                name=CSV_ADAPTER, node=DEFAULT_NODE, config_type="generic"
            )

    def test_config_update_generic_true(self, apiobj, adapter):
        """Pass."""
        data = apiobj.config_refetch(adapter=adapter)
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
