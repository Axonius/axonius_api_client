# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pdb  # noqa
import warnings

import pytest

import axonius_api_client as axonapi

from . import need_creds

tools = axonapi.tools
exceptions = axonapi.exceptions

# FUTURE: adding client with parsed config instead of raw config breaks adapters._get()

CSV_FILENAME = "badwolf.csv"
CSV_FILECONTENTS = ["mac_address,field1", "06:37:53:6E:A2:9C,e", "06:37:53:6E:A2:9C,h"]
CSV_FILECONTENT_STR = "\r\n".join(CSV_FILECONTENTS) + "\r\n"
CSV_FILECONTENT_BYTES = CSV_FILECONTENT_STR.encode()

FAKE_CLIENT_OK = {
    "adapter_name": "fluff1",
    "id": "foobar1",
    "uuid": "abc123",
    "status": True,
}
FAKE_CLIENT_BAD = {
    "adapter_name": "fluff1",
    "id": "foobar2",
    "uuid": "zxy987",
    "status": False,
}
FAKE_CLIENTS = [FAKE_CLIENT_OK, FAKE_CLIENT_BAD]
FAKE_ADAPTER_CLIENTS_OK = {
    "cnx": [FAKE_CLIENT_OK],
    "name": "fluff1",
    "name_raw": "fluff1_adapter",
    "node_name": "master",
    "cnx_count": 2,
    "status": True,
}
FAKE_ADAPTER_CLIENTS_BAD = {
    "cnx": FAKE_CLIENTS,
    "name": "fluff2",
    "name_raw": "fluff2_adapter",
    "node_name": "master",
    "cnx_count": 2,
    "status": False,
}
FAKE_ADAPTER_NOCLIENTS = {
    "cnx": [],
    "name": "fluff3",
    "name_raw": "fluff3_adapter",
    "node_name": "master",
    "cnx_count": 0,
    "status": None,
}
FAKE_ADAPTERS = [
    FAKE_ADAPTER_CLIENTS_BAD,
    FAKE_ADAPTER_CLIENTS_OK,
    FAKE_ADAPTER_NOCLIENTS,
]


def build_test_setting(type, required, name, **kwargs):
    """Pass."""
    setting = {name: {"name": name, "title": name, "type": type, "required": required}}
    setting[name].update(kwargs)
    return setting


def build_test_settings(*args):
    """Pass."""
    settings = {}
    for x in args:
        settings.update(build_test_setting(**x))
    return settings


@pytest.mark.needs_url
@pytest.mark.needs_key_creds
@pytest.mark.parametrize("creds", ["creds_key"], indirect=True, scope="class")
class TestAdapters(object):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, url, creds):
        """Pass."""
        need_creds(creds)

        http = axonapi.Http(url=url, certwarn=False)

        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()

        api = axonapi.api.Adapters(auth=auth)

        assert format(auth.__class__.__name__) in format(api)
        assert format(auth.__class__.__name__) in repr(api)
        assert http.url in format(api)
        assert http.url in repr(api)

        assert isinstance(api.cnx, axonapi.api.mixins.Child)
        assert isinstance(api.cnx, axonapi.api.adapters.Cnx)
        assert api.cnx.__class__.__name__ in format(api.cnx)
        assert api.cnx.__class__.__name__ in repr(api.cnx)

        assert isinstance(api._router, axonapi.api.routers.Router)

        return api

    @pytest.fixture(scope="class")
    def csv_adapter(self, apiobj):
        """Pass."""
        return apiobj.get_single(name="csv", node="master")

    def test__load_filepath(self, apiobj, tmp_path):
        """Pass."""
        test_path = tmp_path / CSV_FILENAME
        test_path.write_bytes(CSV_FILECONTENT_BYTES)
        filename, filecontent = apiobj._load_filepath(test_path)
        assert filename == CSV_FILENAME
        assert filecontent == CSV_FILECONTENT_BYTES

    def test__load_filepath_fail(self, apiobj, tmp_path):
        """Pass."""
        test_path = tmp_path / "fun2.txt"
        with pytest.raises(exceptions.ApiError):
            apiobj._load_filepath(test_path)

    def val_client(self, name, instance, client):
        """Pass."""
        assert tools.is_type.dict(client)
        assert tools.is_type.dict(client["client_config"]) and client["client_config"]
        assert tools.is_type.str(client["uuid"]) and client["uuid"]
        assert tools.is_type.str(client["client_id"])
        if not client["client_id"]:
            msg = "Client for {} has an empty client_id {}"
            msg = msg.format(name, client["client_id"])
            warnings.warn(msg)

        assert tools.is_type.str(client["error"]) or tools.is_type.none(client["error"])
        assert tools.is_type.str(client["node_id"]) and client["node_id"]
        assert tools.is_type.str(client["status"]) and client["status"] in [
            "error",
            "success",
        ]

        if client["status"] == "error":
            assert instance["status"] == "warning"
        assert tools.is_type.str(client["uuid"]) and client["uuid"]

    def val_schema(self, name, schema):
        """Pass."""
        assert tools.is_type.lod(schema["items"]) and schema["items"]
        assert tools.is_type.los(schema["required"])
        for req in schema["required"]:
            item_names = [x["name"] for x in schema["items"]]
            # FUTURE: schema's are defining required items that dont exist in items
            if req not in item_names:
                msg = "Schema for {} has required item {!r} not in defined items {}"
                msg = msg.format(name, req, item_names)
                warnings.warn(msg)

        for item in schema["items"]:
            assert tools.is_type.str(item["name"]) and item["name"]
            assert tools.is_type.str(item["type"]) and item["type"]
            assert tools.is_type.str(item["title"]) and item["title"]
            assert item["type"] in [
                "number",
                "integer",
                "string",
                "bool",
                "array",
                "file",
            ]

    def val_instance(self, name, instance):
        """Pass."""
        assert tools.is_type.str(instance["node_id"]) and instance["node_id"]
        assert (
            tools.is_type.str(instance["unique_plugin_name"])
            and instance["unique_plugin_name"]
        )
        assert tools.is_type.str(instance["node_name"]) and instance["node_name"]
        assert instance["status"] in ["warning", "success", None, ""]
        assert tools.is_type.los(instance["supported_features"])
        assert tools.is_type.list(instance["clients"])
        assert tools.is_type.dict(instance["config"]) and instance["config"]
        assert tools.is_type.dict(instance["schema"]) and instance["schema"]

        self.val_schema(name, instance["schema"])

        assert len(instance["config"]) in [1, 2]
        assert "AdapterBase" in instance["config"]

        for config_name, config in instance["config"].items():
            # AdapterBase: {"config": {}, "schema": {}}
            assert tools.is_type.dict(config["config"]) and config["config"]
            assert (
                tools.is_type.str(config["schema"]["pretty_name"])
                and config["schema"]["pretty_name"]
            )
            assert tools.is_type.dict(config["schema"]) and config["schema"]
            self.val_schema(name, config["schema"])

        for client in instance["clients"]:
            self.val_client(name, instance, client)

    def test__get(self, apiobj):
        """Pass."""
        data = apiobj._get()
        assert tools.is_type.dict(data)
        for name, instances in data.items():
            assert name.endswith("_adapter")
            assert tools.is_type.list(instances)
            for instance in instances:
                self.val_instance(name, instance)

    def test_get(self, apiobj):
        """Pass."""
        data = apiobj.get()
        assert tools.is_type.list(data)
        for x in data:
            assert sorted(list(x)) == sorted(
                [
                    "adv_settings",
                    "cnx",
                    "cnx_bad",
                    "cnx_count",
                    "cnx_count_bad",
                    "cnx_count_ok",
                    "cnx_ok",
                    "cnx_settings",
                    "features",
                    "name",
                    "name_plugin",
                    "name_raw",
                    "node_id",
                    "node_name",
                    "settings",
                    "status",
                    "status_raw",
                ]
            )
            assert tools.is_type.dict(x)
            assert tools.is_type.str(x["name"])
            assert tools.is_type.str(x["name_raw"])
            assert tools.is_type.str(x["name_plugin"])
            assert tools.is_type.str(x["node_name"])
            assert tools.is_type.str(x["node_id"])
            assert tools.is_type.str(x["status_raw"])
            assert tools.is_type.los(x["features"])
            assert tools.is_type.int(x["cnx_count"])
            assert tools.is_type.int(x["cnx_count_ok"])
            assert tools.is_type.int(x["cnx_count_bad"])
            assert tools.is_type.bool(x["status"]) or tools.is_type.none(x["status"])
            assert tools.is_type.dict(x["cnx_settings"])
            assert tools.is_type.dict(x["settings"])
            assert tools.is_type.dict(x["adv_settings"])

            for i in ["cnx", "cnx_ok", "cnx_bad"]:
                assert tools.is_type.list(x[i])
                if x[i]:
                    assert tools.is_type.lod(x[i])

            for s, si in x["cnx_settings"].items():
                assert tools.is_type.dict(si)
                assert tools.is_type.bool(si["required"])
                assert tools.is_type.str(si["name"]) and si["name"]
                assert tools.is_type.str(si["type"]) and si["type"]
                assert tools.is_type.str(si["title"]) and si["title"]

            for s, si in x["settings"].items():
                assert tools.is_type.dict(si)
                assert tools.is_type.bool(si["required"])
                assert tools.is_type.str(si["name"]) and si["name"]
                assert tools.is_type.str(si["type"]) and si["type"]
                assert tools.is_type.str(si["title"]) and si["title"]
                assert "value" in si

            for s, si in x["adv_settings"].items():
                assert tools.is_type.dict(si)
                assert tools.is_type.bool(si["required"])
                assert tools.is_type.str(si["name"]) and si["name"]
                assert tools.is_type.str(si["type"]) and si["type"]
                assert tools.is_type.str(si["title"]) and si["title"]
                assert "value" in si

            for c in x["cnx"]:
                assert sorted(list(c)) == sorted(
                    [
                        "adapter_name",
                        "adapter_name_raw",
                        "adapter_status",
                        "config",
                        "config_raw",
                        "date_fetched",
                        "error",
                        "id",
                        "node_id",
                        "node_name",
                        "status",
                        "status_raw",
                        "uuid",
                    ]
                )
                assert tools.is_type.dict(c)
                assert c["adapter_name"] == x["name"]
                assert c["adapter_name_raw"] == x["name_raw"]
                assert c["adapter_status"] == x["status"]
                assert tools.is_type.dict(c["config"]) and c["config"]
                assert tools.is_type.dict(c["config_raw"]) and c["config_raw"]
                assert tools.is_type.str(c["date_fetched"])
                assert tools.is_type.str(c["error"]) or tools.is_type.none(c["error"])
                assert tools.is_type.str(c["id"])
                assert c["node_id"] == x["node_id"]
                assert c["node_name"] == x["node_name"]
                assert tools.is_type.bool(c["status"])
                assert tools.is_type.str(c["status_raw"])
                assert tools.is_type.str(c["uuid"])

                if c["status"] is False:
                    assert x["status"] is False
                if c["status"] is True:
                    assert x["status"] in [True, False]

                for s, si in c["config"].items():
                    assert tools.is_type.dict(si)
                    assert "value" in si
                    assert tools.is_type.bool(si["required"])
                    assert tools.is_type.str(si["type"]) and si["type"]
                    assert tools.is_type.str(si["title"]) and si["title"]
                    assert si["name"] == s

                    if "enum" in si:
                        assert tools.is_type.los(si["enum"])

                    if si["type"] == "array" and si["value"]:
                        assert tools.is_type.los(si["value"])

    def test_get_single(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.ObjectNotFound):
            apiobj.get_single(name="badwolf")

        with pytest.raises(exceptions.ObjectNotFound):
            apiobj.get_single(name="csv", node="badwolf")

        data = apiobj.get_single(name="csv")
        assert tools.is_type.dict(data)
        assert data["name"] == "csv"

    def test__upload_file(self, apiobj, csv_adapter):
        """Pass."""
        data = apiobj._upload_file(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            field="csv",
            filename=CSV_FILENAME,
            filecontent=CSV_FILECONTENT_BYTES,
        )
        assert tools.is_type.dict(data)
        assert data["uuid"]
        assert data["filename"]

        data = apiobj._upload_file(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            field="csv",
            filename=CSV_FILENAME,
            filecontent=CSV_FILECONTENT_STR,
        )
        assert tools.is_type.dict(data)
        assert data["uuid"]
        assert data["filename"]

    def test_upload_file_str(self, apiobj):
        """Pass."""
        data = apiobj.upload_file_str(
            adapter="csv",
            field="csv",
            filename=CSV_FILENAME,
            filecontent=CSV_FILECONTENT_BYTES,
        )
        assert tools.is_type.dict(data)
        assert data["uuid"]
        assert data["filename"]

        data = apiobj.upload_file_str(
            adapter="csv",
            field="csv",
            filename=CSV_FILENAME,
            filecontent=CSV_FILECONTENT_STR,
        )
        assert tools.is_type.dict(data)
        assert data["uuid"]
        assert data["filename"]

    def test_upload_file_path(self, apiobj, tmp_path):
        """Pass."""
        test_path = tmp_path / CSV_FILENAME
        test_path.write_text(CSV_FILECONTENT_STR)

        data = apiobj.upload_file_path(adapter="csv", field="csv", filepath=test_path)
        assert tools.is_type.dict(data)
        assert tools.is_type.str(data["uuid"])
        assert data["filename"] == CSV_FILENAME

        test_path.write_bytes(CSV_FILECONTENT_BYTES)

        data = apiobj.upload_file_path(adapter="csv", field="csv", filepath=test_path)
        assert tools.is_type.dict(data)
        assert tools.is_type.str(data["uuid"])
        assert data["filename"] == CSV_FILENAME

    def test_filter_by_names_regex(self, apiobj):
        """Pass."""
        data = apiobj.filter_by_names(
            names=".*", use_regex=True, adapters=FAKE_ADAPTERS
        )
        assert tools.is_type.list(data)
        assert len(data) >= 1

        data = apiobj.filter_by_names(
            names=FAKE_ADAPTER_CLIENTS_OK["name"],
            use_regex=False,
            adapters=FAKE_ADAPTERS,
        )
        assert tools.is_type.list(data)
        assert len(data) == 1

    def test_filter_by_names_counts(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.TooFewObjectsFound):
            apiobj.filter_by_names(names="xxx", count_min=1, adapters=FAKE_ADAPTERS)

        data = apiobj.filter_by_names(
            names="xxx", count_min=1, count_error=False, adapters=FAKE_ADAPTERS
        )
        assert tools.is_type.list(data)
        assert len(data) == 0

        with pytest.raises(exceptions.TooManyObjectsFound):
            apiobj.filter_by_names(
                names=".*", count_max=1, use_regex=True, adapters=FAKE_ADAPTERS
            )

        data = apiobj.filter_by_names(
            names=".*",
            count_max=1,
            use_regex=True,
            count_error=False,
            adapters=FAKE_ADAPTERS,
        )
        assert tools.is_type.list(data)
        assert len(data) == 3

    def test_filter_by_nodes_regex(self, apiobj):
        """Pass."""
        data = apiobj.filter_by_nodes(
            nodes="master", use_regex=True, adapters=FAKE_ADAPTERS
        )
        assert tools.is_type.list(data)
        assert len(data) >= 1

        data = apiobj.filter_by_nodes(
            nodes="master", use_regex=False, adapters=FAKE_ADAPTERS
        )
        assert tools.is_type.list(data)
        assert len(data) >= 1

    def test_filter_by_nodes_counts(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.TooFewObjectsFound):
            apiobj.filter_by_nodes(nodes="xxx", count_min=1, adapters=FAKE_ADAPTERS)

        data = apiobj.filter_by_nodes(
            nodes="xxx", count_min=1, count_error=False, adapters=FAKE_ADAPTERS
        )
        assert tools.is_type.list(data)
        assert len(data) == 0

        with pytest.raises(exceptions.TooManyObjectsFound):
            apiobj.filter_by_nodes(
                nodes=".*", count_max=1, use_regex=True, adapters=FAKE_ADAPTERS
            )

        data = apiobj.filter_by_nodes(
            nodes=".*",
            count_max=1,
            count_error=False,
            use_regex=True,
            adapters=FAKE_ADAPTERS,
        )
        assert tools.is_type.list(data)
        assert len(data) == 3

    def test_filter_by_cnx_count(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.TooFewObjectsFound):
            apiobj.filter_by_cnx_count(
                cnx_min=9999, count_min=1, adapters=FAKE_ADAPTERS
            )

        data = apiobj.filter_by_cnx_count(
            cnx_min=9999, count_min=1, count_error=False, adapters=FAKE_ADAPTERS
        )
        assert tools.is_type.list(data)
        assert len(data) == 0

        data = apiobj.filter_by_cnx_count(cnx_min=9999, adapters=FAKE_ADAPTERS)
        assert tools.is_type.list(data)
        assert len(data) == 0

        data = apiobj.filter_by_cnx_count(cnx_min=1, adapters=FAKE_ADAPTERS)
        assert tools.is_type.list(data)
        assert len(data) >= 1

        data = apiobj.filter_by_cnx_count(cnx_max=1, adapters=FAKE_ADAPTERS)
        assert tools.is_type.list(data)
        assert len(data) >= 1

        data = apiobj.filter_by_cnx_count(cnx_max=0, adapters=FAKE_ADAPTERS)
        assert tools.is_type.list(data)
        assert len(data) >= 1

    def test_filter_by_status(self, apiobj):
        """Pass."""
        data = apiobj.filter_by_status(status=True, adapters=FAKE_ADAPTERS)
        assert tools.is_type.list(data)
        for x in data:
            assert x["status"] is True

        data = apiobj.filter_by_status(status=False, adapters=FAKE_ADAPTERS)
        assert tools.is_type.list(data)
        for x in data:
            assert x["status"] is False

        data = apiobj.filter_by_status(status=None, adapters=FAKE_ADAPTERS)
        assert tools.is_type.list(data)
        for x in data:
            assert x["status"] is None

    def _create_csv_client(self, apiobj, csv_adapter):
        """Pass."""
        uploaded = apiobj.upload_file_str(
            adapter=csv_adapter,
            field="csv",
            filename=CSV_FILENAME,
            filecontent=CSV_FILECONTENT_BYTES,
            filecontent_type="text/csv",
        )

        config = {}
        config["is_users_csv"] = False
        config["is_installed_sw"] = False
        config["user_id"] = "private_create_csv_client"
        config["csv"] = uploaded

        added = apiobj.cnx._add(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            config=config,
        )
        assert tools.is_type.dict(added)
        assert tools.is_type.str(added["id"])

        assert added["error"] is None
        assert added["status"] == "success"
        assert added["client_id"] == "private_create_csv_client"
        assert tools.is_type.str(added["id"]) and added["id"]
        return added, config

    def _delete_csv_client(self, apiobj, csv_adapter, added):
        """Pass."""
        deleted = apiobj.cnx._delete(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            cnx_uuid=added["id"],
        )
        assert not deleted

        not_deleted = apiobj.cnx._delete(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            cnx_uuid=added["id"],
        )
        assert not_deleted
        return deleted, not_deleted

    def _check_csv_client(self, apiobj, csv_adapter, config):
        """Pass."""
        checked = apiobj.cnx._check(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            config=config,
        )

        assert tools.is_type.dict(checked)
        assert tools.is_type.str(checked["message"])
        assert checked["status"] == "error"
        assert checked["type"] == "NotImplementedError"
        return checked

    def test_clients__add_check_delete(self, apiobj, csv_adapter):
        """Pass."""
        added, config = self._create_csv_client(apiobj, csv_adapter)
        self._check_csv_client(apiobj, csv_adapter, config)
        self._delete_csv_client(apiobj, csv_adapter, added)

    def test_clients__config_parse(self, apiobj, csv_adapter):
        """Pass."""
        settings = build_test_settings(
            dict(name="test1", type="bool", required=True),
            dict(name="test2", type="string", required=True),
            dict(name="test3", type="integer", required=True),
            dict(name="test4", type="number", required=True),
            dict(name="test5", type="array", required=True),
            dict(name="test6", type="string", required=True, enum=["test6"]),
            dict(name="test7", type="string", required=False),
            dict(name="test8", type="string", required=False, default="test8"),
            dict(name="test9", type="string", required=True, default="test9"),
            dict(name="test10", type="file", required=True),
        )

        parsed_config = apiobj.cnx._config_parse(
            adapter=csv_adapter,
            settings=settings,
            config=dict(
                test1=False,
                test_ignore="",
                test2="test2",
                test3="33",
                test4="44",
                test5=["test5"],
                test6="test6",
                test10={"uuid": "x", "filename": CSV_FILENAME},
            ),
        )
        assert parsed_config == dict(
            test1=False,
            test2="test2",
            test3="33",
            test4="44",
            test5=["test5"],
            test6="test6",
            test8="test8",
            test9="test9",
            test10={"uuid": "x", "filename": CSV_FILENAME},
        )

    def test_clients__config_parse_missing(self, apiobj, csv_adapter):
        """Pass."""
        settings = build_test_settings(dict(name="test1", type="string", required=True))
        with pytest.raises(exceptions.CnxSettingMissing):
            apiobj.cnx._config_parse(adapter=csv_adapter, settings=settings, config={})

    def test_clients__config_parse_badtype(self, apiobj, csv_adapter):
        """Pass."""
        settings = build_test_settings(dict(name="test1", type="string", required=True))
        with pytest.raises(exceptions.CnxSettingInvalidType):
            apiobj.cnx._config_parse(
                adapter=csv_adapter, settings=settings, config=dict(test1=True)
            )

    def test_clients__config_parse_badchoice(self, apiobj, csv_adapter):
        """Pass."""
        settings = build_test_settings(
            dict(name="test1", type="string", required=True, enum=["x"])
        )
        with pytest.raises(exceptions.CnxSettingInvalidChoice):
            apiobj.cnx._config_parse(
                adapter=csv_adapter, settings=settings, config=dict(test1="a")
            )

    def test_clients__config_parse_unknowntype(self, apiobj, csv_adapter):
        """Pass."""
        settings = build_test_settings(
            dict(name="test1", type="badwolf", required=True)
        )
        with pytest.raises(exceptions.CnxSettingUnknownType):
            apiobj.cnx._config_parse(
                adapter=csv_adapter, settings=settings, config=dict(test1="a")
            )

    def test_clients__config_file(self, apiobj):
        """Pass."""
        d = {"uuid": "x", "filename": "x", "extra": "x"}
        assert apiobj.cnx._config_file(d) == {"uuid": "x", "filename": "x"}

    def test_clients__config_check_type(self, apiobj):
        """Pass."""
        schema = {"name": "test", "title": "test", "type": "string", "required": True}
        apiobj.cnx._config_type_check(
            name="test", value="a", type_cb=tools.is_type.str, schema=schema
        )

        with pytest.raises(exceptions.CnxSettingInvalidType):
            apiobj.cnx._config_type_check(
                name="test", value="a", type_cb=tools.is_type.int, schema=schema
            )

    def test_clients__config_file_check_strpath(self, apiobj, csv_adapter, tmp_path):
        """Pass."""
        test_path = tmp_path / CSV_FILENAME
        test_path.write_bytes(CSV_FILECONTENT_BYTES)

        schema = csv_adapter["cnx_settings"]["csv"]

        data = apiobj.cnx._config_file_check(
            name="csv", value=test_path, schema=schema, adapter=csv_adapter
        )
        assert tools.is_type.dict(data)
        assert sorted(list(data)) == sorted(["uuid", "filename"])
        assert all([tools.is_type.str(x) for x in data.values()])
        assert data["filename"] == CSV_FILENAME

        data = apiobj.cnx._config_file_check(
            name="csv", value=format(test_path), schema=schema, adapter=csv_adapter
        )
        assert tools.is_type.dict(data)
        assert sorted(list(data)) == sorted(["uuid", "filename"])
        assert all([tools.is_type.str(x) for x in data.values()])
        assert data["filename"] == CSV_FILENAME

        with pytest.raises(exceptions.ApiError):
            data = apiobj.cnx._config_file_check(
                name="csv",
                value=tmp_path / "missing_badwolf.csv",
                schema=schema,
                adapter=csv_adapter,
            )

        with pytest.raises(exceptions.ApiError):
            data = apiobj.cnx._config_file_check(
                name="csv",
                value=format(tmp_path / "missing_badwolf.csv"),
                schema=schema,
                adapter=csv_adapter,
            )

    def test_clients__config_file_check_dict_uuid(self, apiobj, csv_adapter):
        """Pass."""
        schema = csv_adapter["cnx_settings"]["csv"]

        value = {"uuid": "x", "filename": CSV_FILENAME}
        data = apiobj.cnx._config_file_check(
            name="csv", value=value, schema=schema, adapter=csv_adapter
        )
        assert tools.is_type.dict(data)
        assert data == value

        data = apiobj.cnx._config_file_check(
            name="csv",
            value={"uuid": "x", "filepath": CSV_FILENAME},
            schema=schema,
            adapter=csv_adapter,
        )
        assert tools.is_type.dict(data)
        assert data == value

        data = apiobj.cnx._config_file_check(
            name="csv",
            value={"uuid": "x", "filepath": tools.path.resolve(CSV_FILENAME)},
            schema=schema,
            adapter=csv_adapter,
        )
        assert tools.is_type.dict(data)
        assert data == value

        with pytest.raises(exceptions.CnxSettingMissing):
            data = apiobj.cnx._config_file_check(
                name="csv", value={"uuid": "x"}, schema=schema, adapter=csv_adapter
            )

    def test_clients__config_file_check_dict_filename(self, apiobj, csv_adapter):
        """Pass."""
        schema = csv_adapter["cnx_settings"]["csv"]

        data = apiobj.cnx._config_file_check(
            name="csv",
            value={"filename": CSV_FILENAME, "filecontent": CSV_FILECONTENT_BYTES},
            schema=schema,
            adapter=csv_adapter,
        )
        assert tools.is_type.dict(data)
        assert sorted(list(data)) == sorted(["uuid", "filename"])
        assert all([tools.is_type.str(x) for x in data.values()])
        assert data["filename"] == CSV_FILENAME

        with pytest.raises(exceptions.CnxSettingMissing):
            data = apiobj.cnx._config_file_check(
                name="csv",
                value={"filename": CSV_FILENAME},
                schema=schema,
                adapter=csv_adapter,
            )

        with pytest.raises(exceptions.CnxSettingMissing):
            data = apiobj.cnx._config_file_check(
                name="csv", value={}, schema=schema, adapter=csv_adapter
            )

    def test_clients__config_file_check_dict_filepath(
        self, apiobj, csv_adapter, tmp_path
    ):
        """Pass."""
        test_path = tmp_path / CSV_FILENAME
        test_path.write_bytes(CSV_FILECONTENT_BYTES)

        schema = csv_adapter["cnx_settings"]["csv"]

        data = apiobj.cnx._config_file_check(
            name="csv",
            value={"filepath": test_path},
            schema=schema,
            adapter=csv_adapter,
        )
        assert tools.is_type.dict(data)
        assert sorted(list(data)) == sorted(["uuid", "filename"])
        assert all([tools.is_type.str(x) for x in data.values()])
        assert data["filename"] == CSV_FILENAME

        with pytest.raises(exceptions.CnxSettingMissing):
            data = apiobj.cnx._config_file_check(
                name="csv",
                value={"filename": "x.csv"},
                schema=schema,
                adapter=csv_adapter,
            )

        with pytest.raises(exceptions.CnxSettingMissing):
            data = apiobj.cnx._config_file_check(
                name="csv", value={}, schema=schema, adapter=csv_adapter
            )

    def test_clients__validate_csv_device(self, apiobj):
        """Pass."""
        content = "{},test1\nabc,def\n".format(apiobj.cnx._CSV_FIELDS["device"][0])

        with pytest.warns(None) as record:
            apiobj.cnx._validate_csv(filename=CSV_FILENAME, filecontent=content)

        assert len(record) == 0

        with pytest.warns(None) as record:
            apiobj.cnx._validate_csv(
                filename=CSV_FILENAME, filecontent=content.encode()
            )

        assert len(record) == 0

        content = "test2,test1\nabc,def\n"

        with pytest.warns(exceptions.CnxCsvWarning) as record:
            apiobj.cnx._validate_csv(filename=CSV_FILENAME, filecontent=content)

        assert len(record) == 1

    def test_clients__validate_csv_users(self, apiobj):
        """Pass."""
        content = "{},test1\nabc,def\n".format(apiobj.cnx._CSV_FIELDS["user"][0])

        with pytest.warns(None) as record:
            apiobj.cnx._validate_csv(
                filename=CSV_FILENAME, filecontent=content, is_users=True
            )

        assert len(record) == 0

        content = "test2,test1\nabc,def\n"

        with pytest.warns(exceptions.CnxCsvWarning) as record:
            apiobj.cnx._validate_csv(
                filename=CSV_FILENAME, filecontent=content, is_users=True
            )

        assert len(record) == 1

    def test_clients__validate_csv_sw(self, apiobj):
        """Pass."""
        content = "{},test1\nabc,def\n".format(apiobj.cnx._CSV_FIELDS["sw"][0])

        with pytest.warns(None) as record:
            apiobj.cnx._validate_csv(
                filename=CSV_FILENAME, filecontent=content, is_installed_sw=True
            )

        assert len(record) == 0, "threw warnings"

        content = "test2,test1\nabc,def\n"

        with pytest.warns(exceptions.CnxCsvWarning) as record:
            apiobj.cnx._validate_csv(
                filename=CSV_FILENAME, filecontent=content, is_installed_sw=True
            )

        assert len(record) == 1, "did not throw only one warning"

    def test_clients_get_adapter(self, apiobj):
        """Pass."""
        clients = apiobj.cnx.get(adapter=FAKE_ADAPTER_CLIENTS_OK)
        assert tools.is_type.list(clients)
        assert clients == FAKE_ADAPTER_CLIENTS_OK["cnx"]

    def test_clients_get_str(self, apiobj):
        """Pass."""
        clients = apiobj.cnx.get(adapter="csv")
        assert tools.is_type.list(clients)
        for x in clients:
            assert x["adapter_name"] == "csv"

    def test_clients_get_los(self, apiobj):
        """Pass."""
        clients = apiobj.cnx.get(adapter=["csv", "active_directory"])
        assert tools.is_type.list(clients)
        for x in clients:
            assert x["adapter_name"] in ["csv", "active_directory"]

    def test_clients_get_none(self, apiobj):
        """Pass."""
        clients = apiobj.cnx.get(adapter=None)
        assert tools.is_type.list(clients)

    def test_clients_filter_by_status(self, apiobj):
        """Pass."""
        good = apiobj.cnx.filter_by_status(cnxs=FAKE_CLIENTS, status=True)
        assert good == [FAKE_CLIENTS[0]]

        bad = apiobj.cnx.filter_by_status(cnxs=FAKE_CLIENTS, status=False)
        assert bad == [FAKE_CLIENTS[1]]

    def test_clients_filter_by_ids(self, apiobj):
        """Pass."""
        just1re = apiobj.cnx.filter_by_ids(
            cnxs=FAKE_CLIENTS, ids=FAKE_CLIENTS[0]["id"], use_regex=True
        )
        assert tools.is_type.list(just1re)
        assert just1re == [FAKE_CLIENTS[0]]

        just1 = apiobj.cnx.filter_by_ids(
            cnxs=FAKE_CLIENTS, ids=FAKE_CLIENTS[0]["id"], count_min=1, count_max=1
        )
        assert just1 == [FAKE_CLIENTS[0]]

        with pytest.raises(exceptions.ObjectNotFound):
            apiobj.cnx.filter_by_ids(
                cnxs=FAKE_CLIENTS, ids="badwolfyfakfjlka", count_min=1, count_max=1
            )

    def test_clients_filter_by_uuids(self, apiobj):
        """Pass."""
        just1re = apiobj.cnx.filter_by_uuids(
            cnxs=FAKE_CLIENTS, uuids=FAKE_CLIENTS[0]["uuid"], use_regex=True
        )
        assert tools.is_type.list(just1re)
        assert just1re == [FAKE_CLIENTS[0]]

        just1 = apiobj.cnx.filter_by_uuids(
            cnxs=FAKE_CLIENTS, uuids=FAKE_CLIENTS[0]["uuid"], count_min=1, count_max=1
        )
        assert just1 == [FAKE_CLIENTS[0]]

        with pytest.raises(exceptions.ObjectNotFound):
            apiobj.cnx.filter_by_uuids(
                cnxs=FAKE_CLIENTS, uuids="badwolfyfakfjlka", count_min=1, count_max=1
            )

    def test_clients_start_discovery(self, apiobj):
        """Pass."""
        clients = apiobj.cnx.get(adapter="active_directory")

        if not clients:
            reason = "No active directory clients"
            pytest.skip(reason)

        started = apiobj.cnx.start_discovery(cnxs=clients, error=False)
        assert tools.is_type.list(started)
        assert len(started) == len(clients)

    def test_clients_check(self, apiobj):
        """Pass."""
        clients = apiobj.cnx.get(adapter="active_directory")

        if not clients:
            reason = "No active directory clients"
            pytest.skip(reason)

        for client in clients:
            checked = apiobj.cnx._check(
                adapter_name=client["adapter_name_raw"],
                node_id=client["node_id"],
                config=client["config_raw"],
            )

            if checked:
                data = apiobj.cnx.check(cnxs=client, error=False)
            else:
                data = apiobj.cnx.check(cnxs=client, error=True)

            assert tools.is_type.list(data)
            assert len(data) == 1
            assert tools.is_type.dict(data[0])
            assert data[0]["adapter_name"] == client["adapter_name"]
            assert data[0]["node_name"] == client["node_name"]

            if checked:
                assert data[0]["status"] is False
                assert data[0]["response"]
            else:
                assert data[0]["status"] is True
                assert not data[0]["response"]

            client["config_raw"]["dc_name"] = "badwolf"

            with pytest.raises(exceptions.CnxFailure):
                apiobj.cnx.check(cnxs=client)

            data = apiobj.cnx.check(cnxs=client, error=False)

            assert tools.is_type.list(data)
            assert len(data) == 1
            assert tools.is_type.dict(data[0])
            assert data[0]["adapter_name"] == client["adapter_name"]
            assert data[0]["node_name"] == client["node_name"]
            assert data[0]["status"] is False
            assert data[0]["response"]

    def test_clients_add_delete(self, apiobj):
        """Pass."""
        config = {"dc_name": "BADWOLF", "user": "BADWOLF", "password": "BADWOLF"}
        with pytest.raises(exceptions.CnxFailure):
            apiobj.cnx.add(adapter="active_directory", config=config)

        added = apiobj.cnx.add(adapter="active_directory", config=config, error=False)
        assert tools.is_type.dict(added)

        with pytest.raises(exceptions.CnxFailure):
            apiobj.cnx.check(cnxs=added)

        with pytest.raises(exceptions.CnxDeleteForce):
            apiobj.cnx.delete(cnxs=added, error=True, warning=True)

        with pytest.warns(exceptions.CnxDeleteWarning):
            deleted = apiobj.cnx.delete(
                cnxs=added, force=True, error=True, warning=True, sleep=0
            )

        assert tools.is_type.list(deleted)
        assert len(deleted) == 1

        deleted_item = deleted[0]
        assert deleted_item["adapter_name"] == added["adapter_name"]
        assert deleted_item["node_name"] == added["node_name"]
        assert deleted_item["id"] == added["id"]
        assert deleted_item["uuid"] == added["uuid"]
        assert tools.is_type.bool(deleted_item["delete_success"])
        assert tools.is_type.str(deleted_item["delete_msg"])

        with pytest.warns(exceptions.CnxDeleteWarning):
            with pytest.raises(exceptions.CnxDeleteFailure):
                deleted = apiobj.cnx.delete(
                    cnxs=added, force=True, error=True, warning=True, sleep=0
                )

        with pytest.warns(exceptions.CnxDeleteWarning):
            deleted = apiobj.cnx.delete(
                cnxs=added, force=True, error=False, warning=True, sleep=0
            )

        deleted = apiobj.cnx.delete(
            cnxs=added, force=True, error=False, warning=False, sleep=0
        )

    def delete_added(self, apiobj, added):
        """Pass."""
        deleted = apiobj.cnx.delete(
            cnxs=added, force=True, error=False, warning=False, sleep=0
        )
        assert tools.is_type.list(deleted)
        assert len(deleted) == 1

        deleted_item = deleted[0]
        assert deleted_item["adapter_name"] == added["adapter_name"]
        assert deleted_item["node_name"] == added["node_name"]
        assert deleted_item["id"] == added["id"]
        assert deleted_item["uuid"] == added["uuid"]
        assert tools.is_type.bool(deleted_item["delete_success"])
        assert tools.is_type.str(deleted_item["delete_msg"])

    def test_clients_add_delete_csv_str(self, apiobj):
        """Pass."""
        added = apiobj.cnx.add_csv_str(
            filename=CSV_FILENAME,
            filecontent=CSV_FILECONTENT_BYTES,
            fieldname="STR_" + CSV_FILENAME,
        )
        assert tools.is_type.dict(added)

        self.delete_added(apiobj, added)

    def test_clients_add_delete_csv_file(self, apiobj, tmp_path):
        """Pass."""
        test_path = tmp_path / CSV_FILENAME
        test_path.write_text(CSV_FILECONTENT_STR)

        added = apiobj.cnx.add_csv_file(
            filepath=test_path, fieldname="FILE_" + CSV_FILENAME
        )
        assert tools.is_type.dict(added)

        self.delete_added(apiobj, added)

    def test_clients_add_delete_csv_url(self, apiobj):
        """Pass."""
        added = apiobj.cnx.add_csv_url(
            url="https://localhost/idontexist.csv",
            fieldname="idontexist.csv",
            error=False,
        )
        assert tools.is_type.dict(added)

        self.delete_added(apiobj, added)

    def test_clients_add_delete_csv_share(self, apiobj):
        """Pass."""
        moo = "moo"
        added = apiobj.cnx.add_csv_share(
            share="smb://localhost/thereforeiamnot.csv",
            share_username=moo,
            share_password=moo,
            fieldname="thereforeiamnot.csv",
            error=False,
        )
        assert tools.is_type.dict(added)

        self.delete_added(apiobj, added)
