# -*- coding: utf-8 -*-
"""Test suite."""

import pytest

from axonius_api_client.api import json_api
from axonius_api_client.constants.adapters import CSV_ADAPTER
from axonius_api_client.exceptions import CnxAddError  # ConfigRequired,
from axonius_api_client.exceptions import (
    CnxTestError,
    CnxUpdateError,
    ConfigInvalidValue,
    ConfigUnchanged,
    NotFoundError,
)
from axonius_api_client.tools import combo_dicts

from ...meta import CSV_FILECONTENT_STR, CsvData, CsvKeys, TanData, TanKeys
from ...utils import get_cnx_existing, get_cnx_working


# noinspection PyProtectedMember
def skip_if_no_adapter(api_adapters, adapter):
    """Pass."""
    if not adapter.endswith("_adapter"):
        adapter = f"{adapter}_adapter"

    adapters = api_adapters._get()
    name_map = {x.id: x for x in adapters}
    found = name_map.get(adapter)
    if not found:
        pytest.skip(f"Adapter {adapter!r} not found in {list(name_map)}")
    return found


# noinspection PyMissingOrEmptyDocstring,PyProtectedMember,PyBroadException
class TestCnxBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_adapters):
        return api_adapters

    @pytest.fixture(scope="class")
    def adapter(self, apiobj):
        return apiobj.get_by_name(name=CSV_ADAPTER, get_clients=False)

    @pytest.fixture(scope="function")
    def csv_cnx(self, apiobj):
        skip_if_no_adapter(apiobj, "csv")

        uploaded_file = apiobj.file_upload(
            name=CsvData.adapter_name_raw,
            field_name=CsvData.file_field_name,
            file_name=CsvData.file_name,
            file_content=CsvData.file_contents,
        )
        assert isinstance(uploaded_file, dict)
        assert uploaded_file["uuid"]
        assert uploaded_file["filename"]
        config = combo_dicts(CsvData.config, file_path=uploaded_file)
        core_instance = apiobj.instances.get_core()
        added = apiobj.cnx._add(
            connection=config,
            instance_id=core_instance["id"],
            instance_name=core_instance["name"],
            adapter_name=CsvData.adapter_name_raw,
        )

        data = apiobj.cnx._get(adapter_name=CsvData.adapter_name_raw)

        for cnx in data.cnxs:
            if cnx.uuid == added.id:
                yield cnx
                break
        # fetched = [
        #     x
        #     for x in apiobj.cnx._get(adapter_name=CsvData.adapter_name_raw).cnxs
        #     if x.uuid == added.id
        # ][0]
        # yield fetched

        data = apiobj.cnx._get(adapter_name=CsvData.adapter_name_raw)
        for cnx in data.cnxs:
            user_id = cnx.client_config.get(CsvKeys.user_id) or ""
            if user_id == CsvData.user_id:
                try:
                    apiobj.cnx._delete(
                        uuid=cnx.uuid,
                        adapter_name=cnx.adapter_name_raw,
                        instance_id=cnx.node_id,
                        instance_name=cnx.node_name,
                    )
                except Exception:
                    print(f"Unable to delete connection: {cnx}")
                break

    @pytest.fixture(scope="function")
    def csv_cnx_tunnel(self, apiobj, tunnel_count_check):
        skip_if_no_adapter(apiobj, "csv")
        tunnel = apiobj.instances.get_tunnel_default()

        uploaded_file = apiobj.file_upload(
            name=CsvData.adapter_name_raw,
            field_name=CsvData.file_field_name,
            file_name=CsvData.file_name,
            file_content=CsvData.file_contents,
        )
        assert isinstance(uploaded_file, dict)
        assert uploaded_file["uuid"]
        assert uploaded_file["filename"]
        config = combo_dicts(CsvData.config, file_path=uploaded_file)
        core_instance = apiobj.instances.get_core()
        added = apiobj.cnx._add(
            connection=config,
            tunnel_id=tunnel.id,
            instance_id=core_instance["id"],
            instance_name=core_instance["name"],
            adapter_name=CsvData.adapter_name_raw,
        )
        fetched = [
            x
            for x in apiobj.cnx._get(adapter_name=CsvData.adapter_name_raw).cnxs
            if x.uuid == added.id
        ][0]
        yield fetched

        cnxs = apiobj.cnx._get(adapter_name=CsvData.adapter_name_raw).cnxs
        for cnx in cnxs:
            user_id = cnx.client_config.get(CsvKeys.user_id) or ""
            if user_id == CsvData.user_id and cnx.tunnel_id == tunnel.id:
                try:
                    apiobj.cnx._delete(
                        uuid=cnx.uuid,
                        adapter_name=cnx.adapter_name_raw,
                        instance_id=cnx.node_id,
                        instance_name=cnx.node_name,
                    )
                except Exception:
                    print(f"Unable to delete connection: {cnx}")
                break


# noinspection PyMissingOrEmptyDocstring
class TestCnxPrivate(TestCnxBase):
    pass


@pytest.mark.tunneltests
class TestCnxTunnel(TestCnxBase):
    def test_get_by_adapter_tunnel(self, apiobj, csv_cnx_tunnel):
        skip_if_no_adapter(apiobj, csv_cnx_tunnel.adapter_name_raw)
        data = apiobj.cnx.get_by_adapter(
            adapter_name=csv_cnx_tunnel.adapter_name_raw,
            adapter_node=csv_cnx_tunnel.node_name,
            tunnel=csv_cnx_tunnel.tunnel_id,
        )
        assert isinstance(data, list)
        uuids = [x["uuid"] for x in data]
        assert csv_cnx_tunnel.uuid in uuids
        fake_tunnel = json_api.instances.Tunnel(tunnel_id="xx", tunnel_name="xxx", status="xxx")
        data = apiobj.cnx.get_by_adapter(
            adapter_name=csv_cnx_tunnel.adapter_name_raw,
            adapter_node=csv_cnx_tunnel.node_name,
            tunnel=fake_tunnel,
        )
        assert not data

    def test_add_remove(self, apiobj, tunnel_count_check):
        skip_if_no_adapter(apiobj, TanData.adapter_name)
        tunnel = apiobj.instances.get_tunnel_default()

        with pytest.raises(CnxAddError) as exc:
            apiobj.cnx.add(tunnel=tunnel, adapter_name=TanData.adapter_name, **TanData.config_bad)

        cnx_new = exc.value.cnx_new
        assert isinstance(cnx_new, dict)
        assert cnx_new["uuid"]
        assert cnx_new["id"]

        cnx_deleted = apiobj.cnx.delete_by_id(
            cnx_id=cnx_new["id"], adapter_name=TanData.adapter_name
        )
        assert cnx_deleted.client_id == cnx_new["id"]


# noinspection PyMissingOrEmptyDocstring,PyUnusedLocal
class TestCnxPublic(TestCnxBase):
    def test_add_update_fail(self, apiobj):
        skip_if_no_adapter(apiobj, TanData.adapter_name)
        with pytest.raises(CnxAddError) as exc:
            apiobj.cnx.add(adapter_name=TanData.adapter_name, **TanData.config_bad)

        cnx_new = exc.value.cnx_new
        assert isinstance(cnx_new, dict)
        assert cnx_new["uuid"]
        assert cnx_new["id"]

        config_to_update = combo_dicts(TanData.config_bad, **{TanKeys.password: "moo"})
        with pytest.raises(CnxUpdateError) as exc:
            apiobj.cnx.update_by_id(
                cnx_id=cnx_new["id"], adapter_name=TanData.adapter_name, **config_to_update
            )

        cnx_updated = exc.value.cnx_new
        assert isinstance(cnx_updated, dict)
        assert cnx_updated["uuid"] == cnx_new["uuid"]
        assert cnx_updated["id"] == cnx_new["id"]

        cnx_deleted = apiobj.cnx.delete_by_id(
            cnx_id=cnx_new["id"], adapter_name=TanData.adapter_name
        )
        assert cnx_deleted.client_id == cnx_new["id"]

    def test_update_cnx_err_unchanged(self, apiobj, csv_cnx):
        with pytest.raises(ConfigUnchanged):
            apiobj.cnx.update_cnx(cnx_update=csv_cnx.to_dict_old())

    def test_update_cnx(self, apiobj, csv_cnx):
        config_old = csv_cnx.client_config
        value_old = config_old[CsvKeys.verify_ssl]
        value_new = not value_old
        config_to_update = {CsvKeys.verify_ssl: value_new}

        cnx_updated = apiobj.cnx.update_cnx(cnx_update=csv_cnx.to_dict_old(), **config_to_update)
        config_updated = cnx_updated["config"]
        assert config_updated[CsvKeys.verify_ssl] == value_new

        config_to_revert = {CsvKeys.verify_ssl: value_old}
        cnx_reverted = apiobj.cnx.update_cnx(cnx_update=cnx_updated, **config_to_revert)
        config_reverted = cnx_reverted["config"]
        assert config_reverted[CsvKeys.verify_ssl] == value_old

    def test_update_by_id(self, apiobj, csv_cnx):
        config_old = csv_cnx.client_config
        value_old = config_old[CsvKeys.verify_ssl]
        value_new = not value_old
        config_to_update = {CsvKeys.verify_ssl: value_new}

        cnx_updated = apiobj.cnx.update_by_id(
            cnx_id=csv_cnx.client_id, adapter_name=CsvData.adapter_name, **config_to_update
        )
        config_updated = cnx_updated["config"]
        assert config_updated[CsvKeys.verify_ssl] == value_new

    def test_set_cnx_active(self, apiobj, csv_cnx):
        old_value = csv_cnx.active
        new_value = not old_value
        updated = apiobj.cnx.set_cnx_active(
            cnx=csv_cnx.to_dict_old(), value=new_value, save_and_fetch=False
        )
        assert updated["active"] == new_value
        reverted = apiobj.cnx.set_cnx_active(cnx=updated, value=old_value, save_and_fetch=False)
        assert reverted["active"] == old_value

    def test_set_cnx_label(self, apiobj, csv_cnx):
        old_value = csv_cnx.connection_label
        new_value = "badwolf123"
        updated = apiobj.cnx.set_cnx_label(
            cnx=csv_cnx.to_dict_old(), value=new_value, save_and_fetch=False
        )
        assert updated["connection_label"] == new_value
        reverted = apiobj.cnx.set_cnx_label(cnx=updated, value=old_value, save_and_fetch=False)
        assert reverted["connection_label"] == old_value

    def test_get_by_adapter(self, apiobj):
        skip_if_no_adapter(apiobj, "csv")
        cnxs = apiobj.cnx.get_by_adapter(adapter_name=CSV_ADAPTER)
        assert isinstance(cnxs, list)
        for cnx in cnxs:
            assert isinstance(cnx, dict)
            assert isinstance(cnx["schemas"], dict)

    def test_get_by_adapter_badname(self, apiobj):
        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_adapter(adapter_name="badwolf")

    def test_get_by_adapter_bad_node(self, apiobj):
        skip_if_no_adapter(apiobj, "csv")
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

    def test_get_by_uuid_fail(self, apiobj):
        skip_if_no_adapter(apiobj, "csv")
        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_uuid(cnx_uuid="badwolf", adapter_name="csv")

    def test_get_by_id(self, apiobj):
        cnx = get_cnx_existing(apiobj)
        found = apiobj.cnx.get_by_id(
            cnx_id=cnx["id"],
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
        )
        assert cnx == found

    def test_get_by_label_fail(self, apiobj):
        skip_if_no_adapter(apiobj, "csv")
        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_label(value="badwolf", adapter_name="csv")

    def test_get_by_label(self, apiobj):
        cnx = get_cnx_existing(apiobj)
        # 2023/04/03 - connection_label not returned in config any longer?
        label = cnx["config"].get("connection_label") or cnx.get("connection_label") or ""
        found = apiobj.cnx.get_by_label(
            value=label,
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
        )
        assert cnx == found

    def test_test_by_id(self, apiobj):
        cnx = get_cnx_working(apiobj)
        exp = {"data": None}

        result = apiobj.cnx.test_by_id(
            cnx_id=cnx["id"],
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
        )
        assert result == exp

    def test_test(self, apiobj):
        cnx = get_cnx_working(apiobj)
        exp = {"data": None}
        result = apiobj.cnx.test(
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
            **cnx["config"],
        )
        assert result == exp

    def test_test_fail(self, apiobj):
        skip_if_no_adapter(apiobj, TanData.adapter_name)
        mpass = "badwolf"
        with pytest.raises(CnxTestError):
            apiobj.cnx.test(
                adapter_name=TanData.adapter_name,
                domain=mpass,
                username=mpass,
                password=mpass,
            )

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

        # noinspection PyUnusedLocal
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
        file_path = tmp_path / "test_csv"
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
        file_path = tmp_path / "test_fail.csv"

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
        skip_if_no_adapter(apiobj, "csv")
        config = {
            "user_id": "badwolf",
            "file_path": csv_file_path,
        }
        cnx_added = apiobj.cnx.add(adapter_name=CSV_ADAPTER, **config)
        for k, v in config.items():
            assert v == cnx_added["config"][k]
        client_id = cnx_added["id"]

        del_result = apiobj.cnx.delete_by_id(
            cnx_id=client_id,
            adapter_name=CSV_ADAPTER,
            delete_entities=True,
        )
        assert isinstance(del_result, json_api.adapters.CnxDelete)
        assert del_result.client_id == client_id

        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_id(
                cnx_id=client_id,
                adapter_name=CSV_ADAPTER,
            )

    def test_add_remove_path(self, apiobj, tmp_path):
        skip_if_no_adapter(apiobj, "csv")
        file_path = tmp_path / "test.csv"
        file_path.write_text(CSV_FILECONTENT_STR)
        config = {
            "user_id": "badwolf",
            "file_path": file_path,
        }
        cnx_added = apiobj.cnx.add(adapter_name=CSV_ADAPTER, **config)
        client_id = cnx_added["id"]

        assert isinstance(cnx_added["config"]["file_path"], dict)

        del_result = apiobj.cnx.delete_by_id(
            cnx_id=client_id,
            adapter_name=CSV_ADAPTER,
            delete_entities=True,
        )

        assert isinstance(del_result, json_api.adapters.CnxDelete)
        assert del_result.client_id == client_id

        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_id(
                cnx_id=client_id,
                adapter_name=CSV_ADAPTER,
            )

    def test_add_remove_path_not_exists(self, apiobj, tmp_path):
        skip_if_no_adapter(apiobj, "csv")
        file_path = tmp_path / "bad_test.csv"
        config = {
            "user_id": "badwolf",
            "file_path": file_path,
        }
        with pytest.raises(ConfigInvalidValue):
            apiobj.cnx.add(adapter_name=CSV_ADAPTER, **config)

    def test_add_remove_error(self, apiobj, csv_file_path_broken):
        skip_if_no_adapter(apiobj, "csv")
        config = {
            "user_id": "badwolf",
            "file_path": csv_file_path_broken,
        }
        with pytest.raises(CnxAddError) as exc:
            apiobj.cnx.add(adapter_name=CSV_ADAPTER, **config)

        assert getattr(exc.value, "cnx_new", None)
        assert not hasattr(exc.value, "cnx_old")
        assert getattr(exc.value, "result", None)
        cnx_added = exc.value.cnx_new
        client_id = cnx_added["id"]
        del_result = apiobj.cnx.delete_by_id(
            cnx_id=client_id,
            adapter_name=CSV_ADAPTER,
            delete_entities=True,
        )

        assert isinstance(del_result, json_api.adapters.CnxDelete)
        assert del_result.client_id == client_id

        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_id(
                cnx_id=client_id,
                adapter_name=CSV_ADAPTER,
                retry=2,
            )
