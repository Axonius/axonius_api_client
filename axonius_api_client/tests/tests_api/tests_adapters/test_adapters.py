# -*- coding: utf-8 -*-
"""Test suite."""
import copy

import pytest

from axonius_api_client.api import json_api
from axonius_api_client.constants.adapters import CSV_ADAPTER
from axonius_api_client.exceptions import ApiError, ConfigUnchanged, ConfigUnknown, NotFoundError
from axonius_api_client.tools import dt_now

from ...meta import CSV_FILECONTENT_BYTES, CSV_FILECONTENT_STR, CSV_FILENAME


class TestAdaptersBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_adapters):
        return api_adapters

    @pytest.fixture(scope="class")
    def adapter(self, apiobj):
        return apiobj.get_by_name(name=CSV_ADAPTER, get_clients=False)

    @pytest.fixture(scope="class")
    def history_filters(self, apiobj):
        return apiobj.get_fetch_history_filters()


class TestAdaptersPrivate(TestAdaptersBase):
    def test_private_get(self, apiobj):
        adapters = apiobj._get(get_clients=True)
        assert isinstance(adapters, list) and adapters
        for adapter in adapters:
            assert isinstance(adapter, json_api.adapters.Adapter)
            assert str(adapter)
            assert repr(adapter)
            for adapter_node in adapter.adapter_nodes:
                assert isinstance(adapter_node, json_api.adapters.AdapterNode)
                assert str(adapter_node)
                assert repr(adapter_node)

                an_serial = adapter_node.to_dict_old()
                generic = an_serial["schemas"]["generic"]
                discovery = an_serial["schemas"]["discovery"]
                assert isinstance(generic, dict)
                assert isinstance(discovery, dict)
                assert generic
                assert discovery

                for adapter_node_cnx in adapter_node.cnxs:
                    assert isinstance(adapter_node_cnx, json_api.adapters.AdapterNodeCnx)
                    anc_serial = adapter_node_cnx.to_dict_old()
                    assert isinstance(anc_serial, dict)
                    assert isinstance(adapter_node_cnx.label, str)
                    assert (
                        isinstance(adapter_node_cnx.schema_cnx, dict)
                        and adapter_node_cnx.schema_cnx
                    )
                    assert (
                        isinstance(adapter_node_cnx.schema_cnx_discovery, dict)
                        and adapter_node_cnx.schema_cnx_discovery
                    )
                    assert str(adapter_node_cnx)
                    assert repr(adapter_node_cnx)

    def test_get_labels(self, apiobj):
        ret = apiobj._get_labels()
        assert isinstance(ret, json_api.adapters.CnxLabels)
        assert isinstance(ret.labels, list)
        for x in ret.labels:
            assert isinstance(x, dict)

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

    def test_get_basic(self, apiobj):
        data = apiobj._get_basic()
        assert isinstance(data, json_api.adapters.AdaptersList)
        adapter = data.find_by_name(value=CSV_ADAPTER)
        assert adapter["title"] == "CSV"
        assert adapter["name_raw"] == "csv_adapter"
        assert adapter["name"] == "csv"

        with pytest.raises(NotFoundError):
            data.find_by_name("badwolf")

    def test_get_fetch_history(self, apiobj):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        data = apiobj._get_fetch_history(request_obj=request_obj)
        assert isinstance(data, list)
        for item in data:
            assert isinstance(item, json_api.adapters.AdapterFetchHistory)
            assert str(item)
            assert repr(item)

    def test_get_fetch_history_no_request_obj(self, apiobj):
        data = apiobj._get_fetch_history()
        assert isinstance(data, list)
        for item in data:
            assert isinstance(item, json_api.adapters.AdapterFetchHistory)
            assert str(item)
            assert repr(item)


class TestFetchHistoryModel(TestAdaptersBase):
    def test_set_sort_invalid(self, apiobj):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        with pytest.raises(NotFoundError):
            request_obj.set_sort(value="x", descending=False)

    def test_set_sort_valid(self, apiobj):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        attr = list(request_obj.get_schema_cls().validate_attrs())[0]
        exp = attr
        ret = request_obj.set_sort(value=attr, descending=False)
        assert ret == exp

    def test_set_sort_descending(self, apiobj):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        attr = list(request_obj.get_schema_cls().validate_attrs())[0]
        exp = f"-{attr}"
        ret = request_obj.set_sort(value=attr, descending=True)
        assert ret == exp

    def test_set_sort_empty(self, apiobj):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        attr = None
        exp = None
        ret = request_obj.set_sort(value=attr, descending=True)
        assert ret == exp

    def test_set_filters_invalid_type(self, apiobj, history_filters):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        with pytest.raises(ApiError):
            request_obj.set_filters(history_filters=history_filters, value_type="x", value="v")

    @pytest.mark.parametrize(
        "value_type", json_api.adapters.AdapterFetchHistoryFilters.value_types()
    )
    def test_set_filters_invalid_value(self, apiobj, history_filters, value_type):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        with pytest.raises(NotFoundError):
            request_obj.set_filters(
                history_filters=history_filters, value_type=value_type, value="BaDWolFy a y a"
            )

    @pytest.mark.parametrize(
        "value_type", json_api.adapters.AdapterFetchHistoryFilters.value_types()
    )
    def test_set_filters_valid_value(self, apiobj, history_filters, value_type):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        items = getattr(history_filters, value_type)
        if items:
            if isinstance(items, dict):
                value = list(items.values())[0]
                exp = [value["name_raw"]]
                for value in value.values():
                    ret = request_obj.set_filters(
                        history_filters=history_filters, value_type=value_type, value=value
                    )
                    assert ret == exp
            elif isinstance(items, list):
                value = items[0:2]
                exp = value
                ret = request_obj.set_filters(
                    history_filters=history_filters, value_type=value_type, value=value
                )
                assert ret == exp

    def test_set_filters_adapters_empty(self, apiobj, history_filters):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        values = [None, []]
        exp = []
        for value in values:
            ret = request_obj.set_filters(
                history_filters=history_filters, value_type="adapters", value=value
            )
            assert ret == exp

    def test_set_time_range_empty(self, apiobj):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        exp = json_api.time_range.TimeRange.build()
        ret = request_obj.set_time_range()
        assert ret == exp

    def test_set_time_range_absolute_no_date_start(self, apiobj):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        with pytest.raises(ApiError):
            request_obj.set_time_range(absolute_date_end="2022-01-01")

    def test_set_time_range_absolute_date_start(self, apiobj):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        ret = request_obj.set_time_range(absolute_date_start="2022-01-01")
        assert ret.type == json_api.time_range.DateTypes.absolute.name
        assert ret.date_from.month == 1
        assert ret.date_to.month == dt_now().month
        assert ret.count is None
        assert ret.unit == json_api.time_range.UnitTypes.get_default()

    def test_set_time_range_absolute_date_start_end(self, apiobj):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        ret = request_obj.set_time_range(
            absolute_date_start="2022-01-01", absolute_date_end="2022-02-01"
        )
        assert ret.type == json_api.time_range.DateTypes.absolute.name
        assert ret.date_from.month == 1
        assert ret.date_to.month == 2
        assert ret.count is None
        assert ret.unit == json_api.time_range.UnitTypes.get_default()

    def test_set_time_range_relative_count(self, apiobj):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        ret = request_obj.set_time_range(relative_unit_count=4)
        assert ret.type == json_api.time_range.DateTypes.relative.name
        assert ret.date_from is None
        assert ret.date_to is None
        assert ret.count == 4
        assert ret.unit == json_api.time_range.UnitTypes.get_default()

    def test_set_time_range_relative_type_month(self, apiobj):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        ret = request_obj.set_time_range(
            relative_unit_type=json_api.time_range.UnitTypes.month.name, relative_unit_count=2
        )
        assert ret.type == json_api.time_range.DateTypes.relative.name
        assert ret.date_from is None
        assert ret.date_to is None
        assert ret.count == 2
        assert ret.unit == json_api.time_range.UnitTypes.month.name

    def test_set_time_range_relative_type_invalid(self, apiobj):
        request_obj = json_api.adapters.AdapterFetchHistoryRequest()
        with pytest.raises(ApiError):
            request_obj.set_time_range(relative_unit_type="badwolf", relative_unit_count=1)


class TestAdaptersPublic(TestAdaptersBase):
    def test_get_fetch_history(self, apiobj):
        data = apiobj.get_fetch_history()
        assert isinstance(data, list)
        for item in data:
            assert isinstance(item, json_api.adapters.AdapterFetchHistory)
            assert str(item)
            assert repr(item)

    def test_get_fetch_history_filters(self, apiobj):
        data = apiobj.get_fetch_history_filters()
        assert isinstance(data, json_api.adapters.AdapterFetchHistoryFilters)
        assert str(data)
        assert repr(data)

    def test_get_clients_false(self, apiobj):
        adapters = apiobj.get(get_clients=False)
        for adapter in adapters:
            assert not adapter["cnx"]
            assert not adapter["schemas"]["generic"]
            assert not adapter["schemas"]["specific"]
            assert not adapter["schemas"]["cnx"]

    def test_get_clients_true(self, apiobj):
        adapters = apiobj.get(get_clients=True)
        for adapter in adapters:
            assert adapter["schemas"]["generic"]
            if adapter["schemas"]["specific_name"]:
                assert adapter["schemas"]["specific"]
            assert adapter["schemas"]["cnx"]

    def test_get_by_name(self, apiobj):
        adapter = apiobj.get_by_name(name=CSV_ADAPTER, get_clients=False)
        assert "schemas" in adapter

    def test_get_by_name_basic(self, apiobj):
        adapter = apiobj.get_by_name_basic(value=CSV_ADAPTER)
        assert adapter["title"] == "CSV"
        assert adapter["name_raw"] == "csv_adapter"
        assert adapter["name"] == "csv"

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
        data = apiobj.config_get(name="active_directory", config_type="discovery")
        assert isinstance(data, dict)
        config = data.pop("config")
        assert isinstance(config, dict) and config

        schema = data.pop("schema")
        assert isinstance(schema, dict) and schema

    def test_config_get_specific(self, apiobj):
        data = apiobj.config_get(name="active_directory", config_type="specific")
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
