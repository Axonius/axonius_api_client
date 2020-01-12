# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import warnings

import pytest
import requests

import axonius_api_client as axonapi
from axonius_api_client import constants, exceptions, tools

from .. import utils

CSV_FILENAME = "badwolf.csv"
CSV_FIELDS = ["mac_address", "field1"]
CSV_ROW = ["01:37:53:9E:82:7C", "e"]
CSV_FILECONTENTS = [",".join(CSV_FIELDS), ",".join(CSV_ROW)]
CSV_FILECONTENT_STR = "\r\n".join(CSV_FILECONTENTS) + "\r\n"
CSV_FILECONTENT_BYTES = CSV_FILECONTENT_STR.encode()

FAKE_CNX_OK = {
    "adapter_name": "fluff1",
    "adapter_name_raw": "fluff1_adapter",
    "id": "foobar1",
    "node_name": "xbxb",
    "node_id": "xbxb",
    "uuid": "abc123",
    "status": True,
}
FAKE_CNX_BAD = {
    "adapter_name": "fluff2",
    "adapter_name_raw": "fluff2_adapter",
    "node_name": "xbxb",
    "node_id": "xbxb",
    "id": "foobar2",
    "uuid": "zxy987",
    "status": False,
}
FAKE_CNXS = [FAKE_CNX_OK, FAKE_CNX_BAD]
FAKE_ADAPTER_CNXS_OK = {
    "cnx": [FAKE_CNX_OK],
    "name": "fluff1",
    "name_raw": "fluff1_adapter",
    "node_name": "master",
    "cnx_count": 1,
    "status": True,
}
FAKE_ADAPTER_CNXS_BAD = {
    "cnx": FAKE_CNXS,
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
FAKE_ADAPTERS = [FAKE_ADAPTER_CNXS_BAD, FAKE_ADAPTER_CNXS_OK, FAKE_ADAPTER_NOCLIENTS]
AD_CONFIG_SCHEMA = dict(
    user=CSV_FILENAME,
    password=CSV_FILENAME,
    do_not_fetch_users=False,
    fetch_disabled_devices=True,
    fetch_disabled_users=True,
)


@pytest.fixture(scope="module")
def apiobj(request):
    """Pass."""
    auth = utils.get_auth(request)

    api = axonapi.Adapters(auth=auth)

    utils.check_apiobj(authobj=auth, apiobj=api)

    utils.check_apiobj_children(apiobj=api, cnx=axonapi.api.adapters.Cnx)
    return api


@pytest.fixture(scope="module")
def csv_adapter(apiobj):
    """Pass."""
    return apiobj.get_single(adapter="csv", node="master")


class TestAdapters(object):
    """Pass."""

    def test__get(self, apiobj):
        """Pass."""
        adapters = apiobj._get()
        assert isinstance(adapters, dict)

    def test_get(self, apiobj):
        """Pass."""
        adapters = apiobj.get()
        assert isinstance(adapters, tools.LIST)

    def test_get_single(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.get_single(adapter="badwolf")

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.get_single(adapter="csv", node="badwolf")

        data = apiobj.get_single(adapter="csv")
        assert isinstance(data, dict)
        assert data["name"] == "csv"

        data1 = apiobj.get_single(adapter=data)
        assert data1 == data

    def test__upload_file(self, apiobj, csv_adapter):
        """Pass."""
        data = apiobj._upload_file(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            field="csv",
            name=CSV_FILENAME,
            content=CSV_FILECONTENT_BYTES,
        )
        assert isinstance(data, dict)
        assert data["uuid"]
        assert data["filename"]

        data = apiobj._upload_file(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            field="csv",
            name=CSV_FILENAME,
            content=CSV_FILECONTENT_STR,
        )
        assert isinstance(data, dict)
        assert data["uuid"]
        assert data["filename"]

    def test_upload_file_str(self, apiobj, csv_adapter):
        """Pass."""
        data = apiobj.upload_file_str(
            adapter=csv_adapter,
            field="csv",
            name=CSV_FILENAME,
            content=CSV_FILECONTENT_BYTES,
        )
        assert isinstance(data, dict)
        assert data["uuid"]
        assert data["filename"]

        data = apiobj.upload_file_str(
            adapter=csv_adapter,
            field="csv",
            name=CSV_FILENAME,
            content=CSV_FILECONTENT_STR,
        )
        assert isinstance(data, dict)
        assert data["uuid"]
        assert data["filename"]

    def test_upload_file_path(self, apiobj, tmp_path, csv_adapter):
        """Pass."""
        test_path = tmp_path / CSV_FILENAME
        test_path.write_text(CSV_FILECONTENT_STR)

        data = apiobj.upload_file_path(adapter=csv_adapter, field="csv", path=test_path)
        assert isinstance(data, dict)
        assert isinstance(data["uuid"], tools.STR)
        assert data["filename"] == CSV_FILENAME

        test_path.write_bytes(CSV_FILECONTENT_BYTES)

        data = apiobj.upload_file_path(adapter=csv_adapter, field="csv", path=test_path)
        assert isinstance(data, dict)
        assert isinstance(data["uuid"], tools.STR)
        assert data["filename"] == CSV_FILENAME

    def test_filter_by_names_regex(self, apiobj):
        """Pass."""
        data = apiobj.filter_by_names(
            value=".*", value_regex=True, adapters=FAKE_ADAPTERS
        )
        assert isinstance(data, tools.LIST)
        assert len(data) >= 1

        data = apiobj.filter_by_names(
            value=FAKE_ADAPTER_CNXS_OK["name"], value_regex=True, adapters=FAKE_ADAPTERS
        )
        assert isinstance(data, tools.LIST)
        assert len(data) == 1

    def test_filter_by_names_counts(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.filter_by_names(value="xxx", match_count=1, adapters=FAKE_ADAPTERS)

        data = apiobj.filter_by_names(
            value="xxx", match_count=1, match_error=False, adapters=FAKE_ADAPTERS
        )
        assert isinstance(data, tools.LIST)
        assert len(data) == 0

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.filter_by_names(
                value=".*",
                value_regex=True,
                match_count=1,
                match_error=True,
                adapters=FAKE_ADAPTERS,
            )

        data = apiobj.filter_by_names(
            value=".*",
            value_regex=True,
            match_count=1,
            match_error=False,
            adapters=FAKE_ADAPTERS,
        )
        assert isinstance(data, tools.LIST)
        assert len(data) == 3

    def test_filter_by_nodes_regex(self, apiobj):
        """Pass."""
        data = apiobj.filter_by_nodes(
            value="master", value_regex=True, adapters=FAKE_ADAPTERS
        )
        assert isinstance(data, tools.LIST)
        assert len(data) >= 1

        data = apiobj.filter_by_nodes(
            value="master", value_regex=True, adapters=FAKE_ADAPTERS
        )
        assert isinstance(data, tools.LIST)
        assert len(data) >= 1

    def test_filter_by_nodes_counts(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.filter_by_nodes(
                value="xxx", match_count=1, match_error=True, adapters=FAKE_ADAPTERS
            )

        data = apiobj.filter_by_nodes(
            value="xxx", match_count=1, match_error=False, adapters=FAKE_ADAPTERS
        )
        assert isinstance(data, tools.LIST)
        assert len(data) == 0

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.filter_by_nodes(
                value=".*",
                value_regex=True,
                match_count=1,
                match_error=True,
                adapters=FAKE_ADAPTERS,
            )

        data = apiobj.filter_by_nodes(
            value=".*",
            value_regex=True,
            match_count=1,
            match_error=False,
            adapters=FAKE_ADAPTERS,
        )
        assert isinstance(data, tools.LIST)
        assert len(data) == 3

    def test_filter_by_cnx_count(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.ValueNotFound):
            apiobj.filter_by_cnx_count(
                min_value=9999, match_count=1, match_error=True, adapters=FAKE_ADAPTERS
            )

        data = apiobj.filter_by_cnx_count(adapters=FAKE_ADAPTERS)
        assert isinstance(data, tools.LIST)
        assert len(data) == 3

        data = apiobj.filter_by_cnx_count(max_value=1, adapters=FAKE_ADAPTERS)
        assert isinstance(data, tools.LIST)
        assert len(data) == 2

        data = apiobj.filter_by_cnx_count(
            min_value=2, max_value=2, adapters=FAKE_ADAPTERS
        )
        assert isinstance(data, tools.LIST)
        assert len(data) == 1

        data = apiobj.filter_by_cnx_count(
            min_value=9999, match_count=1, match_error=False, adapters=FAKE_ADAPTERS
        )
        assert isinstance(data, tools.LIST)
        assert len(data) == 0

    def test_filter_by_status(self, apiobj):
        """Pass."""
        data = apiobj.filter_by_status(value=True, adapters=FAKE_ADAPTERS)
        assert isinstance(data, tools.LIST)
        for x in data:
            assert x["status"] is True

        data = apiobj.filter_by_status(value=False, adapters=FAKE_ADAPTERS)
        assert isinstance(data, tools.LIST)
        for x in data:
            assert x["status"] is False

        data = apiobj.filter_by_status(value=[None], adapters=FAKE_ADAPTERS)
        assert isinstance(data, tools.LIST)
        for x in data:
            assert x["status"] is None

        data = apiobj.filter_by_status(value=[False, True], adapters=FAKE_ADAPTERS)
        assert isinstance(data, tools.LIST)
        for x in data:
            assert x["status"] in [False, True]

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.filter_by_status(
                value="x", adapters=FAKE_ADAPTERS, match_count=1, match_error=True
            )


class TestCnx(object):
    """Pass."""

    def _add_csv(self, apiobj, csv_adapter, name):
        """Pass."""
        uploaded = apiobj.upload_file_str(
            adapter=csv_adapter,
            field="csv",
            name=name,
            content=CSV_FILECONTENT_BYTES,
            content_type="text/csv",
        )

        config = {}
        config["is_users_csv"] = False
        config["is_installed_sw"] = False
        config["user_id"] = "private_create_csv"
        config["csv"] = uploaded

        added = apiobj.cnx._add(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            config=config,
        )
        assert isinstance(added, dict)
        assert isinstance(added["id"], tools.STR)

        assert added["error"] is None
        assert added["status"] == "success"
        assert added["client_id"] == "private_create_csv"
        assert isinstance(added["id"], tools.STR) and added["id"]
        return added, config

    def _delete_csv(self, apiobj, csv_adapter, added):
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

    # def test__build_known(self, apiobj, csv_adapter):
    #     """Pass."""
    #     cnxs = apiobj.cnx.get(adapter=csv_adapter)
    #     known = apiobj.cnx._build_known(cnxs)
    #     assert isinstance(known, tools.LIST)
    #     for x in known:
    #         assert isinstance(x, tools.STR)

    def test_refetch(self, apiobj, csv_adapter):
        """Pass."""
        response, config = self._add_csv(
            apiobj, csv_adapter, name="badwolf_public_refetch"
        )

        refetched = apiobj.cnx.refetch(
            adapter_name=csv_adapter["name"],
            node_name=csv_adapter["node_name"],
            response=response,
            filter_method=apiobj.cnx.filter_by_uuids,
            filter_value=response["id"],
        )
        assert refetched["uuid"] == response["id"]

        self._delete_csv(apiobj, csv_adapter, response)

    def test_refetch_fail(self, apiobj, csv_adapter):
        """Pass."""
        response = {"id": "asl;gkj;eoin;oigrnad"}

        with pytest.raises(exceptions.CnxRefetchFailure):
            apiobj.cnx.refetch(
                adapter_name=csv_adapter["name"],
                node_name=csv_adapter["node_name"],
                response=response,
                filter_value="djafskjdf;kjsanhgdsaf",
                filter_method=apiobj.cnx.filter_by_uuids,
                retry=1,
                sleep=0,
            )

    def test__add_check_delete(self, apiobj, csv_adapter):
        """Pass."""
        added, config = self._add_csv(
            apiobj, csv_adapter, name="badwolf_private_add_check_delete"
        )

        response = apiobj.cnx._check(
            adapter_name=csv_adapter["name_raw"],
            node_id=csv_adapter["node_id"],
            config=config,
        )

        assert isinstance(response, requests.Response)

        checked = response.json()

        assert isinstance(checked["message"], tools.STR)
        assert checked["status"] == "error"
        assert checked["type"] == "NotImplementedError"

        self._delete_csv(apiobj, csv_adapter, added)

    def test_add_delete(self, apiobj, csv_adapter):
        """Pass."""
        config = dict(dc_name="badwolf_public_add_delete")
        config.update(AD_CONFIG_SCHEMA)

        adapter = apiobj.get_single("active_directory")

        with pytest.raises(exceptions.CnxConnectFailure) as exc:
            apiobj.cnx.add(adapter=adapter, config=config, parse_config=True, error=True)

        refetched = apiobj.cnx.refetch(
            adapter_name=adapter["name"],
            node_name=adapter["node_name"],
            response=exc.value.response,
            filter_value=exc.value.response["id"],
            filter_method=apiobj.cnx.filter_by_uuids,
        )

        apiobj.cnx.delete(refetched, force=True, sleep=0, warning=False)

    def test_delete_noforce(self, apiobj):
        """Pass."""
        with pytest.raises(exceptions.CnxDeleteForce):
            apiobj.cnx.delete(cnx=FAKE_CNX_BAD, force=False)

    def test_delete_warning(self, apiobj):
        """Pass."""
        with pytest.warns(exceptions.CnxDeleteFailedWarning):
            apiobj.cnx.delete(
                cnx=FAKE_CNX_BAD, force=True, error=False, warning=True, sleep=0
            )

    def test_delete_error(self, apiobj):
        """Pass."""
        with pytest.warns(exceptions.CnxDeleteWarning):
            with pytest.raises(exceptions.CnxDeleteFailed):
                apiobj.cnx.delete(
                    cnx=FAKE_CNX_BAD, force=True, error=True, warning=True, sleep=0
                )

    def test_get_adapter(self, apiobj, csv_adapter):
        """Pass."""
        cnxs = apiobj.cnx.get(adapter=csv_adapter)
        assert isinstance(cnxs, tools.LIST)
        for x in cnxs:
            assert x["adapter_name"] == "csv"

    def test_get_str(self, apiobj):
        """Pass."""
        cnxs = apiobj.cnx.get(adapter="csv")
        assert isinstance(cnxs, tools.LIST)
        for x in cnxs:
            assert x["adapter_name"] == "csv"

    def test_get_list(self, apiobj):
        """Pass."""
        cnxs = apiobj.cnx.get(adapter=["csv", "active_directory"])
        assert isinstance(cnxs, tools.LIST)
        for x in cnxs:
            assert x["adapter_name"] in ["csv", "active_directory"]

    def test_get_none(self, apiobj):
        """Pass."""
        all_adapters = apiobj.get()
        ok_adapters = apiobj.filter_by_status(adapters=all_adapters, value=True)
        cnxs = apiobj.cnx.get(adapter=None)
        assert isinstance(cnxs, tools.LIST)
        for cnx in cnxs:
            assert isinstance(cnx, dict)
        assert len(cnxs) >= len(ok_adapters)

    def test_filter_by_status(self, apiobj):
        """Pass."""
        good = apiobj.cnx.filter_by_status(cnxs=FAKE_CNXS, value=True)
        assert good == [FAKE_CNXS[0]]

        bad = apiobj.cnx.filter_by_status(cnxs=FAKE_CNXS, value=False)
        assert bad == [FAKE_CNXS[1]]

        both = apiobj.cnx.filter_by_status(cnxs=FAKE_CNXS, value=[True, False])
        assert both == FAKE_CNXS

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.cnx.filter_by_status(
                cnxs=FAKE_CNXS, value=["x"], match_count=1, match_error=True
            )

    def test_filter_by_ids(self, apiobj):
        """Pass."""
        just1re = apiobj.cnx.filter_by_ids(
            cnxs=FAKE_CNXS, value=FAKE_CNXS[0]["id"], value_regex=True
        )
        assert isinstance(just1re, tools.LIST)
        assert just1re == [FAKE_CNXS[0]]

        just1 = apiobj.cnx.filter_by_ids(
            cnxs=FAKE_CNXS, value=FAKE_CNXS[0]["id"], value_regex=True, match_count=1
        )
        assert just1 == [FAKE_CNXS[0]]

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.cnx.filter_by_ids(
                cnxs=FAKE_CNXS, value="badwolfyfakfjlka", match_count=1
            )

    def test_filter_by_uuids(self, apiobj):
        """Pass."""
        just1re = apiobj.cnx.filter_by_uuids(
            cnxs=FAKE_CNXS, value=FAKE_CNXS[0]["uuid"], value_regex=True
        )
        assert isinstance(just1re, tools.LIST)
        assert just1re == [FAKE_CNXS[0]]

        just1 = apiobj.cnx.filter_by_uuids(
            cnxs=FAKE_CNXS, value=FAKE_CNXS[0]["uuid"], match_count=1
        )
        assert just1 == [FAKE_CNXS[0]]

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.cnx.filter_by_uuids(
                cnxs=FAKE_CNXS, value="badwolfyfakfjlka", match_count=1
            )

    def test_update_success(self, apiobj):
        """Pass."""
        cnxs = apiobj.cnx.get(adapter=None)
        cnxs = apiobj.cnx.filter_by_status(cnxs=cnxs, value=True)

        if not cnxs:
            reason = "No working connections found!"
            pytest.skip(reason)

        for cnx in cnxs:
            check = apiobj.cnx.check(cnx=cnx, error=False)
            if not check["response_had_error"]:
                response = apiobj.cnx.update(cnx=cnx, error=True)
                assert response["cnx"]["uuid"] != cnx["uuid"]
                return

    def test_update_failure(self, apiobj):
        """Pass."""
        config = dict(dc_name="badwolf_public_update_failure")
        config.update(AD_CONFIG_SCHEMA)

        cnx = apiobj.cnx.add(
            adapter="active_directory", config=config, parse_config=True, error=False
        )

        with pytest.raises(exceptions.CnxConnectFailure) as exc:
            apiobj.cnx.update(cnx=cnx["cnx"], error=True)

        refetched = apiobj.cnx.refetch(
            adapter_name=cnx["cnx"]["adapter_name"],
            node_name=cnx["cnx"]["node_name"],
            response=exc.value.response,
            filter_value=exc.value.response["id"],
            filter_method=apiobj.cnx.filter_by_uuids,
        )

        with pytest.warns(exceptions.CnxDeleteWarning):
            apiobj.cnx.delete(refetched, force=True, sleep=0, warning=True)

    def test_update_parse(self, apiobj):
        """Pass."""
        config = dict(dc_name="badwolf_public_update_parse")
        config.update(AD_CONFIG_SCHEMA)

        cnx = apiobj.cnx.add(
            adapter="active_directory", config=config, parse_config=True, error=False
        )
        with pytest.raises(exceptions.CnxConnectFailure) as exc:
            apiobj.cnx.update(
                cnx=cnx["cnx"], new_config=config, parse_config=True, error=True
            )

        refetched = apiobj.cnx.refetch(
            adapter_name=cnx["cnx"]["adapter_name"],
            node_name=cnx["cnx"]["node_name"],
            response=exc.value.response,
            filter_value=exc.value.response["id"],
            filter_method=apiobj.cnx.filter_by_uuids,
        )

        with pytest.warns(exceptions.CnxDeleteWarning):
            apiobj.cnx.delete(refetched, force=True, sleep=0, warning=True)

    def test_check_success(self, apiobj):
        """Pass."""
        cnxs = apiobj.cnx.get(adapter=None)
        cnxs = apiobj.cnx.filter_by_status(cnxs=cnxs, value=True)

        if not cnxs:
            reason = "No working connections found!"
            pytest.skip(reason)

        for cnx in cnxs:
            checked = apiobj.cnx.check(cnx=cnx, error=False)

            if not checked["response_had_error"]:
                data = apiobj.cnx.check(cnx=cnx, error=True)

                assert isinstance(data, dict)
                assert data["cnx"]["uuid"] == cnx["uuid"]
                assert "response" in data
                return

    def test_check_failure(self, apiobj):
        """Pass."""
        config = dict(dc_name="badwolf_check_failure")
        config.update(AD_CONFIG_SCHEMA)

        cnx = apiobj.cnx.add(adapter="active_directory", config=config, error=False)

        with pytest.raises(exceptions.CnxConnectFailure):
            apiobj.cnx.check(cnx=cnx, error=True)

        apiobj.cnx.delete(cnx=cnx, force=True, warning=False, error=False, sleep=0)

    def test_add_delete_csv_str(self, apiobj):
        """Pass."""
        added = apiobj.cnx.add_csv_str(
            name=CSV_FILENAME,
            content=CSV_FILECONTENT_BYTES,
            field="badwolf_add_csv_str",
        )
        assert isinstance(added, dict)

        apiobj.cnx.delete(
            cnx=added["cnx"], force=True, error=False, warning=False, sleep=0
        )

    def test_add_delete_csv_file(self, apiobj, tmp_path):
        """Pass."""
        test_path = tmp_path / CSV_FILENAME
        test_path.write_text(CSV_FILECONTENT_STR)

        added = apiobj.cnx.add_csv_file(path=test_path, field="badwolf_add_csv_file")
        assert isinstance(added, dict)

        apiobj.cnx.delete(
            cnx=added["cnx"], force=True, error=False, warning=False, sleep=0
        )

    def test_add_delete_csv_url(self, apiobj):
        """Pass."""
        added = apiobj.cnx.add_csv_url(
            url="https://localhost/badwolf_add_csv_url.csv",
            field="badwolf_add_csv_url",
            error=False,
        )
        assert isinstance(added, dict)

        apiobj.cnx.delete(
            cnx=added["cnx"], force=True, error=False, warning=False, sleep=0
        )

    def test_add_delete_csv_share(self, apiobj):
        """Pass."""
        moo = "moo"
        added = apiobj.cnx.add_csv_share(
            share="smb://localhost/badwolf_add_csv_share.csv",
            username=moo,
            password=moo,
            field="badwolf_add_csv_share",
            error=False,
        )
        assert isinstance(added, dict)

        apiobj.cnx.delete(
            cnx=added["cnx"], force=True, error=False, warning=False, sleep=0
        )


class TestValidateCsv(object):
    """Pass."""

    def test_device(self):
        """Pass."""
        content = "{},test1\nabc,def\n".format(constants.CSV_FIELDS["device"][0])

        with pytest.warns(None) as record:
            axonapi.api.adapters.validate_csv(name=CSV_FILENAME, content=content)

        assert len(record) == 0

    def test_device_bytes(self):
        """Pass."""
        content = "{},test1\nabc,def\n".format(constants.CSV_FIELDS["device"][0])

        with pytest.warns(None) as record:
            axonapi.api.adapters.validate_csv(
                name=CSV_FILENAME, content=content.encode()
            )

        assert len(record) == 0

    def test_device_warn(self):
        """Pass."""
        content = "test2,test1\nabc,def\n"

        with pytest.warns(exceptions.CnxCsvWarning) as record:
            axonapi.api.adapters.validate_csv(name=CSV_FILENAME, content=content)

        assert len(record) == 1

    def test_users(self):
        """Pass."""
        content = "{},test1\nabc,def\n".format(constants.CSV_FIELDS["user"][0])

        with pytest.warns(None) as record:
            axonapi.api.adapters.validate_csv(
                name=CSV_FILENAME, content=content, is_users=True
            )

        assert len(record) == 0

    def test_users_warn(self):
        """Pass."""
        content = "test2,test1\nabc,def\n"

        with pytest.warns(exceptions.CnxCsvWarning) as record:
            axonapi.api.adapters.validate_csv(
                name=CSV_FILENAME, content=content, is_users=True
            )

        assert len(record) == 1

    def test_sw(self):
        """Pass."""
        content = "{},test1\nabc,def\n".format(constants.CSV_FIELDS["sw"][0])

        with pytest.warns(None) as record:
            axonapi.api.adapters.validate_csv(
                name=CSV_FILENAME, content=content, is_installed_sw=True
            )

        assert len(record) == 0, "threw warnings"

    def test_sw_warn(self):
        """Pass."""
        content = "test2,test1\nabc,def\n"

        with pytest.warns(exceptions.CnxCsvWarning) as record:
            axonapi.api.adapters.validate_csv(
                name=CSV_FILENAME, content=content, is_installed_sw=True
            )

        assert len(record) == 1, "did not throw only one warning"


class TestParserCnxConfig(object):
    """Pass."""

    def test_ignore(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="string", required=True))

        config = dict(test1="test1", ignore="x")

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1="test1")

    def test_enum(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(
            test1=dict(name="test1", type="string", required=True, enum=["test1"])
        )

        config = dict(test1="test1")

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1="test1")

    def test_enum_invalidchoice(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(
            test1=dict(name="test1", type="string", required=True, enum=["test1"])
        )

        config = dict(test1="badwolf")

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.CnxSettingInvalidChoice):
            parser.parse(adapter=csv_adapter, settings=fake_settings)

    def test_unchanged(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="string", required=True))

        config = dict(test1=constants.SETTING_UNCHANGED)

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1=constants.SETTING_UNCHANGED)

    def test_string(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="string", required=True))

        config = dict(test1="test1")

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1="test1")

    def test_number(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="number", required=True))

        config = dict(test1="2")

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1=2)

    def test_integer(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="integer", required=True))

        config = dict(test1="2")

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1=2)

    def test_bool(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="bool", required=True))

        config = dict(test1=False)

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1=False)

    def test_optional_default(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(
            test1=dict(name="test1", type="string", default="x", required=False)
        )

        config = dict()

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1="x")

    def test_optional_missing(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="string", required=False))

        config = dict()

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict()

    def test_required_default(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(
            test1=dict(name="test1", type="string", default="x", required=True)
        )

        config = dict()

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1="x")

    def test_required_missing(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="string", required=True))

        config = dict()

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.CnxSettingMissing):
            parser.parse(adapter=csv_adapter, settings=fake_settings)

    def test_array(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="array", required=True))

        config = dict(test1=["test1"])

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1=["test1"])

    def test_array_comma(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="array", required=True))

        config = dict(test1="test1,test2,test3")

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1=["test1", "test2", "test3"])

    def test_array_invalidtype(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="array", required=True))

        config = dict(test1=[True])

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.CnxSettingInvalidType):
            parser.parse(adapter=csv_adapter, settings=fake_settings)

    def test_badtype(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="string", required=True))

        config = dict(test1=True)

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.CnxSettingInvalidType):
            parser.parse(adapter=csv_adapter, settings=fake_settings)

    def test_unknowntype(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="badwolf", required=True))

        config = dict(test1="a")

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.CnxSettingUnknownType):
            parser.parse(adapter=csv_adapter, settings=fake_settings)

    def test_file_badtype(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="file", required=True))

        config = dict(test1=["X"])

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.CnxSettingInvalidType):
            parser.parse(adapter=csv_adapter, settings=fake_settings)

    def test_file_missing(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="file", required=True))

        config = dict(test1={})

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.CnxSettingFileMissing):
            parser.parse(adapter=csv_adapter, settings=fake_settings)

    def test_file_uuid(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="file", required=True))

        config = dict(test1={"uuid": "x", "filename": "x", "ignore": "me"})

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1={"uuid": "x", "filename": "x"})

    def test_filename(self, apiobj, csv_adapter, monkeypatch):
        """Pass."""
        #
        def mock_upload_file(**kwargs):
            """Pass."""
            return {"uuid": "x", "filename": "badwolf"}

        monkeypatch.setattr(apiobj, "_upload_file", mock_upload_file)

        fake_settings = dict(test1=dict(name="test1", type="file", required=True))

        config = dict(test1={"filename": "x", "filecontent": "x"})

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1={"uuid": "x", "filename": "badwolf"})

    def test_filepath(self, apiobj, csv_adapter, monkeypatch, tmp_path):
        """Pass."""
        #
        def mock_upload_file(**kwargs):
            """Pass."""
            return {"uuid": "x", "filename": CSV_FILENAME}

        monkeypatch.setattr(apiobj, "_upload_file", mock_upload_file)

        fake_settings = dict(test1=dict(name="test1", type="file", required=True))

        test_path = tmp_path / CSV_FILENAME
        test_path.write_text(CSV_FILECONTENT_STR)

        config = dict(test1={"filepath": test_path})

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1={"uuid": "x", "filename": CSV_FILENAME})

    def test_filepath_str(self, apiobj, csv_adapter, monkeypatch, tmp_path):
        """Pass."""
        #
        def mock_upload_file(**kwargs):
            """Pass."""
            return {"uuid": "x", "filename": CSV_FILENAME}

        monkeypatch.setattr(apiobj, "_upload_file", mock_upload_file)

        fake_settings = dict(test1=dict(name="test1", type="file", required=True))

        test_path = tmp_path / CSV_FILENAME
        test_path.write_text(CSV_FILECONTENT_STR)

        config = dict(test1=format(test_path))

        parser = axonapi.api.adapters.ParserCnxConfig(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(adapter=csv_adapter, settings=fake_settings)

        assert parsed_config == dict(test1={"uuid": "x", "filename": CSV_FILENAME})


class TestParserAdapters(object):
    """Pass."""

    def test_adapters(self, apiobj):
        """Pass."""
        raw = apiobj._get()
        parser = axonapi.api.adapters.ParserAdapters(raw=raw, parent=apiobj)
        adapters = parser.parse()
        assert isinstance(adapters, tools.LIST)
        for adapter in adapters:
            self.validate_adapter(adapter)

    def validate_cnx(self, aname, aname_raw, astatus, anid, anname, cnx):
        """Pass."""
        assert isinstance(cnx, dict)
        adapter_name = cnx.pop("adapter_name")
        adapter_name_raw = cnx.pop("adapter_name_raw")
        adapter_status = cnx.pop("adapter_status")
        config = cnx.pop("config")
        config_raw = cnx.pop("config_raw")
        date_fetched = cnx.pop("date_fetched")
        error = cnx.pop("error")
        cid = cnx.pop("id")
        node_id = cnx.pop("node_id")
        node_name = cnx.pop("node_name")
        status = cnx.pop("status")
        status_raw = cnx.pop("status_raw")
        uuid = cnx.pop("uuid")

        assert adapter_name == aname
        assert adapter_name_raw == aname_raw
        assert adapter_status == astatus
        assert isinstance(config, dict) and config
        assert isinstance(config_raw, dict) and config_raw
        assert isinstance(date_fetched, tools.STR)
        assert isinstance(error, tools.STR) or error is None
        assert isinstance(cid, tools.STR)
        assert node_id == anid
        assert node_name == anname
        assert isinstance(status, bool)
        assert isinstance(status_raw, tools.STR)
        assert isinstance(uuid, tools.STR)

        if status is False:
            assert astatus is False

        if status is True:
            assert astatus in [True, False]

        assert not cnx

    def validate_settings(self, settings, check_value):
        """Pass."""
        for name, item in settings.items():
            item_name = item.pop("name")
            item_type = item.pop("type")
            item_title = item.pop("title")
            item_format = item.pop("format", "")
            item_description = item.pop("description", "")
            item_enum = item.pop("enum", [])
            item_default = item.pop("default", "")
            item_items = item.pop("items", {})
            item_required = item.pop("required")

            if check_value:
                item_value = item.pop("value")
                assert isinstance(item_value, tools.SIMPLE) or item_value in [None, []]

            assert isinstance(item_name, tools.STR) and item_name
            assert isinstance(item_type, tools.STR) and item_type
            assert isinstance(item_title, tools.STR) and item_title
            assert isinstance(item_items, dict)
            assert isinstance(item_default, tools.SIMPLE) or item_default in [None, []]
            assert isinstance(item_enum, tools.LIST)
            for x in item_enum:
                assert isinstance(x, tools.STR)
            assert isinstance(item_format, tools.STR)
            assert isinstance(item_description, tools.STR)
            assert isinstance(item_required, bool)
            assert item_type in ["number", "integer", "string", "bool", "array", "file"]
            assert not item

    def validate_adapter(self, adapter):
        """Pass."""
        assert isinstance(adapter, dict)

        adv_settings = adapter.pop("adv_settings")
        cnx = adapter.pop("cnx")
        cnx_bad = adapter.pop("cnx_bad")
        cnx_count = adapter.pop("cnx_count")
        cnx_count_bad = adapter.pop("cnx_count_bad")
        cnx_count_ok = adapter.pop("cnx_count_ok")
        cnx_ok = adapter.pop("cnx_ok")
        cnx_settings = adapter.pop("cnx_settings")
        features = adapter.pop("features")
        name = adapter.pop("name")
        name_plugin = adapter.pop("name_plugin")
        name_raw = adapter.pop("name_raw")
        node_id = adapter.pop("node_id")
        node_name = adapter.pop("node_name")
        settings = adapter.pop("settings")
        status = adapter.pop("status")
        status_raw = adapter.pop("status_raw")

        assert isinstance(name, tools.STR)
        assert isinstance(name_raw, tools.STR)
        assert isinstance(name_plugin, tools.STR)
        assert isinstance(node_name, tools.STR)
        assert isinstance(node_id, tools.STR)
        assert isinstance(status_raw, tools.STR)
        assert isinstance(features, tools.LIST)
        for x in features:
            assert isinstance(x, tools.STR)
        assert isinstance(cnx_count, tools.INT)
        assert isinstance(cnx_count_ok, tools.INT)
        assert isinstance(cnx_count_bad, tools.INT)
        assert isinstance(status, bool) or status is None
        assert isinstance(cnx_settings, dict)
        assert isinstance(settings, dict)
        assert isinstance(adv_settings, dict)

        self.validate_settings(settings, True)
        self.validate_settings(adv_settings, True)
        self.validate_settings(cnx_settings, False)

        for cnxs in [cnx, cnx_ok, cnx_bad]:
            assert isinstance(cnxs, tools.LIST)
            for connection in [x for x in cnxs if x]:
                self.validate_cnx(
                    aname=name,
                    aname_raw=name_raw,
                    anid=node_id,
                    anname=node_name,
                    astatus=status,
                    cnx=connection,
                )

        assert not adapter


class TestRawAdapters(object):
    """Pass."""

    def test_adapters(self, apiobj):
        """Pass."""
        adapters = apiobj._get()
        assert isinstance(adapters, dict)

        for name, instances in adapters.items():
            assert name.endswith("_adapter")
            assert isinstance(instances, tools.LIST)

            for instance in instances:
                self.validate_instance(name, instance)

    def validate_client(self, name, client, instance_status):
        """Pass."""
        assert isinstance(client, dict)

        client_config = client.pop("client_config")
        uuid = client.pop("uuid")
        client_id = client.pop("client_id")
        error = client.pop("error")
        node_id = client.pop("node_id")
        status = client.pop("status")
        date_fetched = client.pop("date_fetched")

        assert isinstance(client_config, dict) and client_config
        assert isinstance(client_id, tools.STR)
        assert isinstance(date_fetched, tools.STR)
        assert isinstance(uuid, tools.STR) and uuid

        if not client_id:
            msg = "Client for {} has an empty client_id {}"
            msg = msg.format(name, client_id)
            warnings.warn(msg)

        assert isinstance(error, tools.STR) or error is None
        assert isinstance(node_id, tools.STR) and node_id
        assert isinstance(status, tools.STR) and status in [
            "warning",
            "error",
            "success",
        ]

        if status == "error":
            assert instance_status == "warning"

        assert not client

    def validate_schema(self, name, schema):
        """Pass."""
        assert isinstance(schema, dict)

        items = schema.pop("items")
        required = schema.pop("required")
        schema_type = schema.pop("type")

        assert isinstance(items, tools.LIST) and items
        assert isinstance(required, tools.LIST)
        assert schema_type == "array"

        for req in required:
            assert isinstance(req, tools.STR)
            item_names = [x["name"] for x in items]

            if req not in item_names:
                msg = "Schema for {} has required item {!r} not in defined items {}"
                msg = msg.format(name, req, item_names)
                warnings.warn(msg)

        for item in items:
            assert isinstance(item, dict)
            item_name = item.pop("name")
            item_type = item.pop("type")
            item_title = item.pop("title")
            item_format = item.pop("format", "")
            item_description = item.pop("description", "")
            item_enum = item.pop("enum", [])
            item_default = item.pop("default", "")
            item_items = item.pop("items", {})
            item_req = item.pop("required", False)

            assert isinstance(item_name, tools.STR) and item_name
            assert isinstance(item_type, tools.STR) and item_type
            assert isinstance(item_title, tools.STR) and item_title
            assert isinstance(item_items, dict)
            assert isinstance(item_default, tools.SIMPLE) or item_default is None
            assert isinstance(item_enum, tools.LIST)
            for x in item_enum:
                assert isinstance(x, tools.STR)
            assert isinstance(item_format, tools.STR)
            assert isinstance(item_description, tools.STR)
            assert isinstance(item_req, bool)
            assert item_type in ["number", "integer", "string", "bool", "array", "file"]
            assert not item

        assert not schema

    def validate_instance(self, name, instance):
        """Pass."""
        node_id = instance.pop("node_id")
        unique_plugin_name = instance.pop("unique_plugin_name")
        node_name = instance.pop("node_name")
        supported_features = instance.pop("supported_features")
        clients = instance.pop("clients")
        config = instance.pop("config")
        schema = instance.pop("schema")
        status = instance.pop("status")

        assert not instance

        assert isinstance(node_id, tools.STR) and node_id
        assert isinstance(unique_plugin_name, tools.STR) and unique_plugin_name
        assert isinstance(node_name, tools.STR) and node_name
        assert status in ["warning", "success", None, ""]
        assert isinstance(supported_features, tools.LIST)
        for x in supported_features:
            assert isinstance(x, tools.STR)
        assert isinstance(clients, tools.LIST)
        assert isinstance(config, dict) and config
        assert isinstance(schema, dict) and schema

        self.validate_schema(name, schema)

        assert len(config) in [1, 2]
        assert "AdapterBase" in config

        for config_name, item in config.items():
            item_config = item.pop("config")
            item_schema = item.pop("schema")
            item_pretty_name = item_schema.pop("pretty_name")

            assert isinstance(item_config, dict) and item_config
            assert isinstance(item_pretty_name, tools.STR) and item_pretty_name
            assert isinstance(item_schema, dict) and item_schema

            self.validate_schema(name, item_schema)

            assert not item

        for client in clients:
            self.validate_client(name, client, status)
