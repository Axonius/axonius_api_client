# -*- coding: utf-8 -*-
"""Test suite."""

import pytest

from axonius_api_client.api import json_api
from axonius_api_client.constants.adapters import CSV_ADAPTER
from axonius_api_client.exceptions import CnxAddError  # CnxUpdateError,
from axonius_api_client.exceptions import (
    CnxGoneError,
    CnxTestError,
    ConfigInvalidValue,
    ConfigRequired,
    ConfigUnchanged,
    NotFoundError,
)

from ...meta import CSV_FILECONTENT_STR
from ...utils import get_cnx_broken, get_cnx_existing, get_cnx_working


class TestCnxBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_adapters):
        return api_adapters

    @pytest.fixture(scope="class")
    def adapter(self, apiobj):
        return apiobj.get_by_name(name=CSV_ADAPTER, get_clients=False)


class TestCnxPrivate(TestCnxBase):
    pass


class TestCnxPublic(TestCnxBase):
    def test_get_by_adapter(self, apiobj):
        cnxs = apiobj.cnx.get_by_adapter(adapter_name=CSV_ADAPTER)
        assert isinstance(cnxs, list)
        for cnx in cnxs:
            assert isinstance(cnx, dict)
            assert isinstance(cnx["schemas"], dict)

    def test_get_by_adapter_badname(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_adapter(adapter_name="badwolf")

    def test_get_by_adapter_badnode(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_adapter(adapter_name=CSV_ADAPTER, adapter_node="badwolf")

    def test_get_by_uuid(self, apiobj):
        cnx = get_cnx_existing(apiobj)
        found = apiobj.cnx.get_by_uuid(
            cnx_uuid=cnx["uuid"],
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
        )
        assert cnx == found

    def test_get_by_id(self, apiobj):
        cnx = get_cnx_existing(apiobj)
        found = apiobj.cnx.get_by_id(
            cnx_id=cnx["id"],
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
        )
        assert cnx == found

    def test_get_by_label_fail(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_label(value="badwolf", adapter_name="aws")

    def test_get_by_label(self, apiobj):
        cnx = get_cnx_existing(apiobj)
        found = apiobj.cnx.get_by_label(
            value=cnx["config"].get("connection_label") or "",
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
        )
        assert cnx == found

    def test_test_by_id(self, apiobj):
        cnx = get_cnx_working(apiobj)
        result = apiobj.cnx.test_by_id(
            cnx_id=cnx["id"],
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
        )
        assert result is True

    def test_test(self, apiobj):
        cnx = get_cnx_working(apiobj)
        result = apiobj.cnx.test(
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
            **cnx["config"],
        )
        assert result is True

    def test_test_fail(self, apiobj):
        mpass = "badwolf"
        with pytest.raises(CnxTestError):
            apiobj.cnx.test(
                adapter_name="tanium",
                domain=mpass,
                username=mpass,
                password=mpass,
            )

    def test_test_fail_no_domain(self, apiobj):
        with pytest.raises(ConfigRequired):
            apiobj.cnx.test(adapter_name="tanium", username="x")

    def test_update_cnx_nochange(self, apiobj):
        cnx = get_cnx_broken(apiobj)
        with pytest.raises(ConfigUnchanged):
            apiobj.cnx.update_cnx(cnx_update=cnx)

    def test_update_cnx(self, apiobj):
        cnx = get_cnx_working(apiobj, name="tanium")
        config_key = "last_reg_mins"
        value_orig = cnx["config"].get(config_key) or 0
        value_to_set = 60 if not isinstance(value_orig, int) else value_orig + 10

        cnx_update = apiobj.cnx.update_cnx(cnx_update=cnx, **{config_key: value_to_set})
        assert cnx_update["config"][config_key] == value_to_set

        cnx_reset = apiobj.cnx.update_by_id(
            cnx_id=cnx_update["id"],
            adapter_name=cnx_update["adapter_name"],
            adapter_node=cnx_update["node_name"],
            **{config_key: value_orig or 0},
        )
        assert cnx_reset["config"][config_key] == value_orig

        with pytest.raises(CnxGoneError):
            apiobj.cnx.update_cnx(cnx_update=cnx, **{config_key: 9999})

        cnx_final = apiobj.cnx.get_by_id(
            cnx_id=cnx_reset["id"], adapter_name=cnx_reset["adapter_name"]
        )
        assert cnx_final["config"][config_key] == value_orig

    # XXX this needs work
    # def test_update_cnx_error(self, apiobj):
    #     config_key = "https_proxy"

    #     cnx = get_cnx_working(apiobj=apiobj, reqkeys=["domain", config_key])

    #     config_orig = cnx["config"]
    #     value_orig = config_orig.get(config_key)
    #     value_to_set = "badwolf"

    #     with pytest.raises(CnxUpdateError) as exc:
    #         apiobj.cnx.update_cnx(cnx_update=cnx, **{config_key: value_to_set})

    #     assert getattr(exc.value, "cnx_new", None)
    #     assert getattr(exc.value, "cnx_old", None)
    #     assert getattr(exc.value, "result", None)
    #     assert exc.value.cnx_new["config"][config_key] == value_to_set
    #     assert exc.value.cnx_old["config"].get(config_key) == value_orig

    #     cnx_reset = apiobj.cnx.update_cnx(
    #     cnx_update=exc.value.cnx_new, **{config_key: value_orig})
    #     assert cnx_reset["config"][config_key] == value_orig

    def test_cb_file_upload_fail(self, apiobj, csv_file_path, monkeypatch):
        mock_return = {"filename": "badwolf", "uuid": "badwolf"}

        def mock_file_upload(name, field_name, file_name, file_content, node):
            return mock_return

        monkeypatch.setattr(apiobj, "file_upload", mock_file_upload)
        with pytest.raises(ConfigInvalidValue):
            apiobj.cnx.cb_file_upload(
                value=[{"badwolf": "badwolf"}],
                schema={"name": "badwolf"},
                callbacks={"adapter_name": "badwolf", "adapter_node": "badwolf"},
                source="badwolf",
            )

    def test_cb_file_upload_dict(self, apiobj, csv_file_path, monkeypatch):
        mock_return = {"filename": "badwolf", "uuid": "badwolf"}

        def mock_file_upload(name, field_name, file_name, file_content, node):
            return mock_return

        monkeypatch.setattr(apiobj, "file_upload", mock_file_upload)
        result = apiobj.cnx.cb_file_upload(
            value=csv_file_path,
            schema={"name": "badwolf"},
            callbacks={"adapter_name": "badwolf", "adapter_node": "badwolf"},
            source="badwolf",
        )
        assert result == csv_file_path

    def test_cb_file_upload_dict_fail(self, apiobj, monkeypatch):
        mock_return = {"filename": "badwolf", "uuid": "badwolf"}

        def mock_file_upload(name, field_name, file_name, file_content, node):
            return mock_return

        monkeypatch.setattr(apiobj, "file_upload", mock_file_upload)
        with pytest.raises(ConfigInvalidValue):
            apiobj.cnx.cb_file_upload(
                value={"badwolf": "badwolf"},
                schema={"name": "badwolf"},
                callbacks={"adapter_name": "badwolf", "adapter_node": "badwolf"},
                source="badwolf",
            )

    def test_cb_file_upload_path(self, apiobj, tmp_path, monkeypatch):
        file_path = tmp_path / "test.csv"
        file_path.write_text(CSV_FILECONTENT_STR)

        def mock_file_upload(name, field_name, file_name, file_content, node):
            return {"filename": file_name, "uuid": "badwolf"}

        monkeypatch.setattr(apiobj, "file_upload", mock_file_upload)
        result = apiobj.cnx.cb_file_upload(
            value=file_path,
            schema={"name": "badwolf"},
            callbacks={"adapter_name": "badwolf", "adapter_node": "badwolf"},
            source="badwolf",
        )
        assert result == {"filename": str(file_path.name), "uuid": "badwolf"}

    def test_cb_file_upload_path_fail(self, apiobj, tmp_path, monkeypatch):
        file_path = tmp_path / "test.csv"

        def mock_file_upload(name, field_name, file_name, file_content, node):
            return {"filename": file_name, "uuid": "badwolf"}

        monkeypatch.setattr(apiobj, "file_upload", mock_file_upload)
        with pytest.raises(ConfigInvalidValue):
            apiobj.cnx.cb_file_upload(
                value=file_path,
                schema={"name": "badwolf"},
                callbacks={"adapter_name": "badwolf", "adapter_node": "badwolf"},
                source="badwolf",
            )

    def test_cb_file_upload_str(self, apiobj, tmp_path, monkeypatch):
        file_path = tmp_path / "testcsv"
        file_path.write_text(CSV_FILECONTENT_STR)

        def mock_file_upload(name, field_name, file_name, file_content, node):
            return {"filename": file_name, "uuid": "badwolf"}

        monkeypatch.setattr(apiobj, "file_upload", mock_file_upload)
        result = apiobj.cnx.cb_file_upload(
            value=str(file_path),
            schema={"name": "badwolf"},
            callbacks={"adapter_name": "badwolf", "adapter_node": "badwolf"},
            source="badwolf",
        )
        assert result == {"filename": str(file_path.name), "uuid": "badwolf"}

    def test_cb_file_upload_str_fail(self, apiobj, tmp_path, monkeypatch):
        file_path = tmp_path / "testfail.csv"

        def mock_file_upload(name, field_name, file_name, file_content, node):
            return {"filename": file_name, "uuid": "badwolf"}

        monkeypatch.setattr(apiobj, "file_upload", mock_file_upload)
        with pytest.raises(ConfigInvalidValue):
            apiobj.cnx.cb_file_upload(
                value=str(file_path),
                schema={"name": "badwolf"},
                callbacks={"adapter_name": "badwolf", "adapter_node": "badwolf"},
                source="badwolf",
            )

    def test_add_remove(self, apiobj, csv_file_path):
        config = {
            "user_id": "badwolf",
            "file_path": csv_file_path,
            # "is_users": False,
            # "is_installed_sw": False,
            # "s3_use_ec2_attached_instance_profile": False,
        }
        cnx_added = apiobj.cnx.add(adapter_name=CSV_ADAPTER, **config)
        for k, v in config.items():
            assert v == cnx_added["config"][k]

        del_result = apiobj.cnx.delete_by_id(
            cnx_id=cnx_added["id"],
            adapter_name=CSV_ADAPTER,
            delete_entities=True,
        )

        assert isinstance(del_result, json_api.adapters.CnxDelete)
        assert del_result.client_id == "{'client_id': 'badwolf'}"

        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_id(
                cnx_id=cnx_added["id"],
                adapter_name=CSV_ADAPTER,
            )

    def test_add_remove_path(self, apiobj, tmp_path):
        file_path = tmp_path / "test.csv"
        file_path.write_text(CSV_FILECONTENT_STR)
        config = {
            "user_id": "badwolf",
            "file_path": file_path,
        }
        cnx_added = apiobj.cnx.add(adapter_name=CSV_ADAPTER, **config)

        assert isinstance(cnx_added["config"]["file_path"], dict)

        del_result = apiobj.cnx.delete_by_id(
            cnx_id=cnx_added["id"],
            adapter_name=CSV_ADAPTER,
            delete_entities=True,
        )

        assert isinstance(del_result, json_api.adapters.CnxDelete)
        assert del_result.client_id == "{'client_id': 'badwolf'}"

        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_id(
                cnx_id=cnx_added["id"],
                adapter_name=CSV_ADAPTER,
            )

    def test_add_remove_path_notexists(self, apiobj, tmp_path):
        file_path = tmp_path / "badtest.csv"
        config = {
            "user_id": "badwolf",
            "file_path": file_path,
        }
        with pytest.raises(ConfigInvalidValue):
            apiobj.cnx.add(adapter_name=CSV_ADAPTER, **config)

    def test_add_remove_error(self, apiobj, csv_file_path_broken):
        config = {
            "user_id": "badwolf",
            "file_path": csv_file_path_broken,
            # SANE_DEFAULTS handles these now:
            # "is_users": False,
            # "is_installed_sw": False,
            # "s3_use_ec2_attached_instance_profile": False,
        }
        with pytest.raises(CnxAddError) as exc:
            apiobj.cnx.add(adapter_name=CSV_ADAPTER, **config)

        assert getattr(exc.value, "cnx_new", None)
        assert not hasattr(exc.value, "cnx_old")
        assert getattr(exc.value, "result", None)
        cnx_added = exc.value.cnx_new

        del_result = apiobj.cnx.delete_by_id(
            cnx_id=cnx_added["id"],
            adapter_name=CSV_ADAPTER,
            delete_entities=True,
        )

        assert isinstance(del_result, json_api.adapters.CnxDelete)
        assert del_result.client_id == "{'client_id': 'badwolf'}"

        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_id(
                cnx_id=cnx_added["id"],
                adapter_name=CSV_ADAPTER,
                retry=2,
            )
