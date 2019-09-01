# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
import requests

import axonius_api_client as axonapi

from . import need_creds

tools = axonapi.tools

CSV_FILENAME = "input.csv"
CSV_FILECONTENT_BYTES = b"\xef\xbb\xbffield1,field2,mac,field4,field5\r\na,b,0:00,d,e\r\nf,g,06:37:53:6E:A2:9C,h,i\r\n"  # noqa
CSV_FILECONTENT_STR = CSV_FILECONTENT_BYTES.decode()


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
@pytest.mark.needs_any_creds
@pytest.mark.parametrize(
    "creds", ["creds_user", "creds_key"], indirect=True, scope="class"
)
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

        assert isinstance(api.clients, axonapi.api.mixins.Child)
        assert isinstance(api.clients, axonapi.api.adapters.Clients)
        assert api.clients.__class__.__name__ in format(api.clients)
        assert api.clients.__class__.__name__ in repr(api.clients)

        assert isinstance(api._router, axonapi.api.routers.Router)

        return api

    @pytest.fixture(scope="class")
    def all_adapters(self, apiobj):
        """Pass."""
        data = apiobj.get()
        assert tools.is_type.list(data)
        for x in data:
            assert tools.is_type.dict(x)
            assert tools.is_type.str(x["name"])
            assert tools.is_type.str(x["name_raw"])
            assert tools.is_type.str(x["name_plugin"])
            assert tools.is_type.str(x["node_name"])
            assert tools.is_type.str(x["node_id"])
            assert tools.is_type.str(x["status"])
            assert tools.is_type.list(x["features"])
            assert tools.is_type.int(x["client_count"])
            assert tools.is_type.int(x["client_count_ok"])
            assert tools.is_type.int(x["client_count_bad"])
            assert tools.is_type.bool(x["status_bool"]) or tools.is_type.none(
                x["status_bool"]
            )
            assert tools.is_type.dict(x["settings_clients"])
            assert tools.is_type.dict(x["settings_adapter"])
            assert tools.is_type.dict(x["settings_advanced"])
            assert tools.is_type.list(x["clients"])

            for s, si in x["settings_clients"].items():
                assert tools.is_type.dict(si)
                assert tools.is_type.bool(si["required"])

            for s, si in x["settings_adapter"].items():
                assert tools.is_type.dict(si)
                assert tools.is_type.bool(si["required"])
                assert "value" in si

            for s, si in x["settings_advanced"].items():
                assert tools.is_type.dict(si)
                assert tools.is_type.bool(si["required"])
                assert "value" in si

            for c in x["clients"]:
                assert tools.is_type.dict(c)
                assert tools.is_type.dict(c["settings_raw"])
                assert c["node_name"] == x["node_name"]
                assert c["node_id"] == x["node_id"]
                assert c["adapter"] == x["name"]
                assert c["adapter_raw"] == x["name_raw"]
                assert c["adapter_status"] == x["status"]
                assert c["adapter_features"] == x["features"]
                assert tools.is_type.bool(c["status_bool"])
                if c["status_bool"] is False:
                    assert x["status_bool"] is False
                if c["status_bool"] is True:
                    assert x["status_bool"] in [True, False]
                assert tools.is_type.dict(c["settings"])
                for s, si in c["settings"].items():
                    assert tools.is_type.dict(si)
                    assert "value" in si
                    assert tools.is_type.bool(si["required"])
                    assert tools.is_type.str(si["type"])
                    assert tools.is_type.str(si["title"])
                    assert si["name"] == s
                    if "enum" in si:
                        assert tools.is_type.list(si["enum"])
                    if si["type"] == "array" and si["value"]:
                        assert tools.is_type.list(si["value"])

        return data

    @pytest.fixture(scope="class")
    def working_client(self, apiobj, all_adapters):
        """Pass."""
        for adapter in all_adapters:
            working_clients = apiobj.clients.get(adapter=adapter, status=True)
            if working_clients:
                return working_clients[0]
        reason = "No adapters found with working clients"
        pytest.skip(reason=reason)

    @pytest.fixture(scope="class")
    def csv_adapter(self, apiobj, all_adapters):
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
        with pytest.raises(axonapi.exceptions.ApiError):
            apiobj._load_filepath(test_path)

    def test__get(self, apiobj):
        """Pass."""
        data = apiobj._get()
        assert tools.is_type.dict(data)
        # TODO do asserts for structure

    def test_get(self, apiobj, all_adapters):
        """Pass."""
        data = apiobj.get(adapters=all_adapters)
        assert data == all_adapters

    def test_get_single(self, apiobj, all_adapters):
        """Pass."""
        with pytest.raises(axonapi.exceptions.ObjectNotFound):
            apiobj.get_single(name="badwolf")

        with pytest.raises(axonapi.exceptions.ObjectNotFound):
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

    def test_upload_file_str(self, apiobj, csv_adapter):
        """Pass."""
        data = apiobj.upload_file_str(
            adapter=csv_adapter,
            field="csv",
            filename=CSV_FILENAME,
            filecontent=CSV_FILECONTENT_BYTES,
        )
        assert tools.is_type.dict(data)
        assert data["uuid"]
        assert data["filename"]

        data = apiobj.upload_file_str(
            adapter=csv_adapter,
            field="csv",
            filename=CSV_FILENAME,
            filecontent=CSV_FILECONTENT_STR,
        )
        assert tools.is_type.dict(data)
        assert data["uuid"]
        assert data["filename"]

    def test_upload_file_path(self, apiobj, csv_adapter, tmp_path):
        """Pass."""
        test_path = tmp_path / CSV_FILENAME
        test_path.write_text(CSV_FILECONTENT_STR)

        data = apiobj.upload_file_path(
            adapter=csv_adapter, field="csv", filepath=test_path
        )
        assert tools.is_type.dict(data)
        assert tools.is_type.str(data["uuid"])
        assert data["filename"] == CSV_FILENAME

        test_path.write_bytes(CSV_FILECONTENT_BYTES)

        data = apiobj.upload_file_path(
            adapter=csv_adapter, field="csv", filepath=test_path
        )
        assert tools.is_type.dict(data)
        assert tools.is_type.str(data["uuid"])
        assert data["filename"] == CSV_FILENAME

    def test_get_by_names_regex(self, apiobj, all_adapters):
        """Pass."""
        data = apiobj.get_by_names(names=".*", use_regex=True, adapters=all_adapters)
        assert tools.is_type.list(data)
        assert len(data) >= 1

        data = apiobj.get_by_names(names="csv", use_regex=False, adapters=all_adapters)
        assert tools.is_type.list(data)
        assert len(data) == 1

    def test_get_by_names_counts(self, apiobj, all_adapters):
        """Pass."""
        with pytest.raises(axonapi.exceptions.TooFewObjectsFound):
            apiobj.get_by_names(names="xxx", count_min=1, adapters=all_adapters)

        data = apiobj.get_by_names(
            names="xxx", count_min=1, count_error=False, adapters=all_adapters
        )
        assert tools.is_type.list(data)
        assert len(data) == 0

        with pytest.raises(axonapi.exceptions.TooManyObjectsFound):
            apiobj.get_by_names(
                names=".*", count_max=1, use_regex=True, adapters=all_adapters
            )

        data = apiobj.get_by_names(
            names=".*",
            count_max=1,
            use_regex=True,
            count_error=False,
            adapters=all_adapters,
        )
        assert tools.is_type.list(data)
        assert len(data) >= 1

    def test_get_by_nodes_regex(self, apiobj, all_adapters):
        """Pass."""
        data = apiobj.get_by_nodes(
            nodes="master", use_regex=True, adapters=all_adapters
        )
        assert tools.is_type.list(data)
        assert len(data) >= 1

        data = apiobj.get_by_nodes(
            nodes="master", use_regex=False, adapters=all_adapters
        )
        assert tools.is_type.list(data)
        assert len(data) >= 1

    def test_get_by_nodes_counts(self, apiobj, all_adapters):
        """Pass."""
        with pytest.raises(axonapi.exceptions.TooFewObjectsFound):
            apiobj.get_by_nodes(nodes="xxx", count_min=1, adapters=all_adapters)

        data = apiobj.get_by_nodes(
            nodes="xxx", count_min=1, count_error=False, adapters=all_adapters
        )
        assert tools.is_type.list(data)
        assert len(data) == 0

        with pytest.raises(axonapi.exceptions.TooManyObjectsFound):
            apiobj.get_by_nodes(
                nodes=".*", count_max=1, use_regex=True, adapters=all_adapters
            )

        data = apiobj.get_by_nodes(
            nodes=".*",
            count_max=1,
            count_error=False,
            use_regex=True,
            adapters=all_adapters,
        )
        assert tools.is_type.list(data)
        assert len(data) >= 0

    def test_get_by_features_regex(self, apiobj, all_adapters):
        """Pass."""
        data = apiobj.get_by_features(
            features="ScannerAdapter", use_regex=True, adapters=all_adapters
        )
        assert tools.is_type.list(data)
        assert len(data) >= 1

        data = apiobj.get_by_features(
            features="ScannerAdapter", use_regex=False, adapters=all_adapters
        )
        assert tools.is_type.list(data)
        assert len(data) >= 1

    def test_get_by_features_counts(self, apiobj, all_adapters):
        """Pass."""
        with pytest.raises(axonapi.exceptions.TooFewObjectsFound):
            apiobj.get_by_features(features="xxx", count_min=1, adapters=all_adapters)

        data = apiobj.get_by_features(
            features="xxx", count_min=1, count_error=False, adapters=all_adapters
        )
        assert tools.is_type.list(data)
        assert len(data) == 0

        with pytest.raises(axonapi.exceptions.TooManyObjectsFound):
            apiobj.get_by_features(
                features=".*", use_regex=True, count_max=1, adapters=all_adapters
            )

        data = apiobj.get_by_features(
            features=None, count_max=1, count_error=False, adapters=all_adapters
        )
        assert tools.is_type.list(data)
        assert len(data) == 0

    def test_get_by_client_count(self, apiobj, all_adapters):
        """Pass."""
        with pytest.raises(axonapi.exceptions.TooFewObjectsFound):
            apiobj.get_by_client_count(
                client_min=9999, count_min=1, adapters=all_adapters
            )

        data = apiobj.get_by_client_count(
            client_min=9999, count_min=1, count_error=False, adapters=all_adapters
        )
        assert tools.is_type.list(data)
        assert len(data) == 0

        data = apiobj.get_by_client_count(client_min=9999, adapters=all_adapters)
        assert tools.is_type.list(data)
        assert len(data) == 0

        data = apiobj.get_by_client_count(client_min=1, adapters=all_adapters)
        assert tools.is_type.list(data)
        assert len(data) >= 1

        data = apiobj.get_by_client_count(client_max=1, adapters=all_adapters)
        assert tools.is_type.list(data)
        assert len(data) >= 1

        data = apiobj.get_by_client_count(client_max=0, adapters=all_adapters)
        assert tools.is_type.list(data)
        assert len(data) >= 1

    def test_get_by_status(self, apiobj, all_adapters):
        """Pass."""
        data = apiobj.get_by_status(status=True, adapters=all_adapters)
        assert tools.is_type.list(data)
        for x in data:
            assert x["status_bool"] is True

        data = apiobj.get_by_status(status=False, adapters=all_adapters)
        assert tools.is_type.list(data)
        for x in data:
            assert x["status_bool"] is False

        data = apiobj.get_by_status(status=None, adapters=all_adapters)
        assert tools.is_type.list(data)
        for x in data:
            assert x["status_bool"] is None

    def test_clients__add_check_delete(self, apiobj, csv_adapter):
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
        config["user_id"] = "csv"
        config["csv"] = uploaded

        added = apiobj.clients._add(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            config=config,
        )
        assert tools.is_type.dict(added)
        assert tools.is_type.str(added["id"])
        assert added["error"] is None
        assert added["status"] == "success"
        assert added["client_id"] == "csv"

        checked = apiobj.clients._check(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            config=config,
        )
        assert isinstance(checked, requests.Response)
        checked_data = checked.json()
        assert tools.is_type.dict(checked_data)
        assert tools.is_type.str(checked_data["message"])
        assert checked_data["status"] == "error"
        assert checked_data["type"] == "NotImplementedError"

        deleted = apiobj.clients._delete(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            client_id=added["id"],
        )
        assert not deleted

        with pytest.raises(axonapi.exceptions.JsonError):
            apiobj.clients._delete(
                adapter_name=csv_adapter["name_raw"],
                node_id=csv_adapter["node_id"],
                client_id=added["id"],
            )

    def test_clients__check_working(self, apiobj, working_client):
        """Pass."""
        checked = apiobj.clients._check(
            adapter_name=working_client["adapter_raw"],
            node_id=working_client["node_id"],
            config=working_client["settings_raw"],
        )
        assert isinstance(checked, requests.Response)
        assert not checked.text

    def test_clients__parse_config(self, apiobj, csv_adapter):
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
        )

        parsed_config = apiobj.clients._parse_config(
            adapter=csv_adapter,
            settings_client=settings,
            config=dict(
                test1=False,
                test_ignore="",
                test2="test2",
                test3="33",
                test4="44",
                test5=["test5"],
                test6="test6",
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
        )

    def test_clients__parse_config_missing(self, apiobj, csv_adapter):
        """Pass."""
        settings = build_test_settings(dict(name="test1", type="string", required=True))
        with pytest.raises(axonapi.exceptions.ClientSettingMissingError):
            apiobj.clients._parse_config(
                adapter=csv_adapter, settings_client=settings, config={}
            )

    def test_clients__parse_config_badtype(self, apiobj, csv_adapter):
        """Pass."""
        settings = build_test_settings(dict(name="test1", type="string", required=True))
        with pytest.raises(axonapi.exceptions.ClientSettingInvalidTypeError):
            apiobj.clients._parse_config(
                adapter=csv_adapter, settings_client=settings, config=dict(test1=True)
            )

    def test_clients__parse_config_badchoice(self, apiobj, csv_adapter):
        """Pass."""
        settings = build_test_settings(
            dict(name="test1", type="string", required=True, enum=["x"])
        )
        with pytest.raises(axonapi.exceptions.ClientSettingInvalidChoiceError):
            apiobj.clients._parse_config(
                adapter=csv_adapter, settings_client=settings, config=dict(test1="a")
            )

    def test_clients__parse_config_unknowntype(self, apiobj, csv_adapter):
        """Pass."""
        settings = build_test_settings(
            dict(name="test1", type="badwolf", required=True)
        )
        with pytest.raises(axonapi.exceptions.ClientSettingUnknownError):
            apiobj.clients._parse_config(
                adapter=csv_adapter, settings_client=settings, config=dict(test1="a")
            )

    def test_clients__upload_dict(self, apiobj):
        """Pass."""
        d = {"uuid": "x", "filename": "x", "extra": "x"}
        assert apiobj.clients._upload_dict(d) == {"uuid": "x", "filename": "x"}
