# -*- coding: utf-8 -*-
"""Test suite."""
import io

import pytest

from axonius_api_client.constants import CSV_ADAPTER, DEFAULT_NODE
from axonius_api_client.exceptions import (
    CnxAddError,
    CnxGoneError,
    CnxTestError,
    CnxUpdateError,
    ConfigInvalidValue,
    ConfigRequired,
    ConfigUnchanged,
    NotFoundError,
)

from ...meta import CSV_FILECONTENT_STR
from ...utils import get_cnx_broken, get_cnx_existing, get_cnx_working


class TestCnxBase:
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_adapters):
        """Pass."""
        return api_adapters

    @pytest.fixture(scope="class")
    def adapter(self, apiobj):
        """Pass."""
        return apiobj.get_by_name(name=CSV_ADAPTER, node=DEFAULT_NODE)


class TestCnxPrivate(TestCnxBase):
    """Pass."""


class TestCnxPublic(TestCnxBase):
    """Pass."""

    def test_get_by_adapter(self, apiobj):
        """Pass."""
        cnxs = apiobj.cnx.get_by_adapter(
            adapter_name=CSV_ADAPTER, adapter_node=DEFAULT_NODE
        )
        assert isinstance(cnxs, list)
        for cnx in cnxs:
            assert isinstance(cnx, dict)
            assert isinstance(cnx["schemas"], dict)

    def test_get_by_adapter_badname(self, apiobj):
        """Pass."""
        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_adapter(adapter_name="badwolf", adapter_node=DEFAULT_NODE)

    def test_get_by_adapter_badnode(self, apiobj):
        """Pass."""
        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_adapter(adapter_name=CSV_ADAPTER, adapter_node="badwolf")

    def test_get_by_uuid(self, apiobj):
        """Pass."""
        cnx = get_cnx_existing(apiobj)
        found = apiobj.cnx.get_by_uuid(
            cnx_uuid=cnx["uuid"],
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
        )
        assert cnx == found

    def test_get_by_id(self, apiobj):
        """Pass."""
        cnx = get_cnx_existing(apiobj)
        found = apiobj.cnx.get_by_id(
            cnx_id=cnx["id"],
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
        )
        assert cnx == found

    def test_test_by_id(self, apiobj):
        """Pass."""
        cnx = get_cnx_working(apiobj)
        result = apiobj.cnx.test_by_id(
            cnx_id=cnx["id"],
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
        )
        assert not result

    def test_test(self, apiobj):
        """Pass."""
        cnx = get_cnx_working(apiobj)
        result = apiobj.cnx.test(
            adapter_name=cnx["adapter_name"],
            adapter_node=cnx["node_name"],
            **cnx["config"],
        )
        assert not result

    def test_test_fail(self, apiobj):
        """Pass."""
        mpass = "badwolf"
        with pytest.raises(CnxTestError):
            apiobj.cnx.test(
                adapter_name="tanium",
                adapter_node=DEFAULT_NODE,
                domain=mpass,
                username=mpass,
                password=mpass,
            )

    def test_test_fail_no_domain(self, apiobj):
        """Pass."""
        with pytest.raises(ConfigRequired):
            apiobj.cnx.test(
                adapter_name="tanium", adapter_node=DEFAULT_NODE, username="x",
            )

    def test_update_cnx_nochange(self, apiobj):
        """Pass."""
        cnx = get_cnx_broken(apiobj)
        with pytest.raises(ConfigUnchanged):
            apiobj.cnx.update_cnx(cnx_update=cnx)

    def test_update_cnx(self, apiobj):
        """Pass."""
        cnx = get_cnx_working(apiobj)
        old_label = cnx["config"].get("connection_label", None)
        gone_test = "gone test"
        if old_label == "badwolf":
            new_label = "badwolf1"
        else:
            new_label = "badwolf"

        cnx_update = apiobj.cnx.update_cnx(cnx_update=cnx, connection_label=new_label)
        assert cnx_update["config"]["connection_label"] == new_label

        cnx_reset = apiobj.cnx.update_by_id(
            cnx_id=cnx_update["id"],
            adapter_name=cnx_update["adapter_name"],
            adapter_node=cnx_update["node_name"],
            connection_label=old_label,
        )
        assert cnx_reset["config"]["connection_label"] == old_label

        with pytest.raises(CnxGoneError):
            apiobj.cnx.update_cnx(cnx_update=cnx, connection_label=gone_test)

        cnx_final = apiobj.cnx.get_by_id(
            cnx_id=cnx_reset["id"], adapter_name=cnx_reset["adapter_name"]
        )
        assert cnx_final["config"]["connection_label"] == old_label

    def test_update_cnx_error(self, apiobj):
        """Pass."""
        cnx = get_cnx_working(apiobj=apiobj, reqkeys=["https_proxy"])
        old_https_proxy = cnx["config"].get("https_proxy")
        new_https_proxy = "badwolf"

        with pytest.raises(CnxUpdateError) as exc:
            apiobj.cnx.update_cnx(cnx_update=cnx, https_proxy=new_https_proxy)

        assert getattr(exc.value, "cnx_new", None)
        assert getattr(exc.value, "cnx_old", None)
        assert getattr(exc.value, "result", None)
        assert exc.value.cnx_new["config"]["https_proxy"] == new_https_proxy
        assert exc.value.cnx_old["config"].get("https_proxy") == old_https_proxy

        cnx_reset = apiobj.cnx.update_cnx(
            cnx_update=exc.value.cnx_new, https_proxy=old_https_proxy
        )
        assert cnx_reset["config"]["https_proxy"] == old_https_proxy

    def test_add_remove(self, apiobj, csv_file_path):
        """Pass."""
        config = {
            "user_id": "badwolf",
            "file_path": csv_file_path,
            # "is_users": False,
            # "is_installed_sw": False,
            # "s3_use_ec2_attached_instance_profile": False,
        }
        cnx_added = apiobj.cnx.add(
            adapter_name=CSV_ADAPTER, adapter_node=DEFAULT_NODE, **config
        )
        for k, v in config.items():
            assert v == cnx_added["config"][k]

        del_result = apiobj.cnx.delete_by_id(
            cnx_id=cnx_added["id"],
            adapter_name=CSV_ADAPTER,
            adapter_node=DEFAULT_NODE,
            delete_entities=True,
        )

        assert del_result == {"client_id": "badwolf"}

        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_id(
                cnx_id=cnx_added["id"],
                adapter_name=CSV_ADAPTER,
                adapter_node=DEFAULT_NODE,
            )

    def test_add_remove_str_error(self, apiobj):
        """Pass."""
        config = {
            "user_id": "badwolf",
            "file_path": io.StringIO("BADwoLF"),
        }
        with pytest.raises(CnxAddError) as exc:
            apiobj.cnx.add(adapter_name=CSV_ADAPTER, adapter_node=DEFAULT_NODE, **config)

        assert getattr(exc.value, "cnx_new", None)
        assert not hasattr(exc.value, "cnx_old")
        assert getattr(exc.value, "result", None)
        cnx_added = exc.value.cnx_new

        del_result = apiobj.cnx.delete_by_id(
            cnx_id=cnx_added["id"],
            adapter_name=CSV_ADAPTER,
            adapter_node=DEFAULT_NODE,
            delete_entities=True,
        )

        assert del_result == {"client_id": "badwolf"}

        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_id(
                cnx_id=cnx_added["id"],
                adapter_name=CSV_ADAPTER,
                adapter_node=DEFAULT_NODE,
                retry=2,
            )

    def test_add_remove_path(self, apiobj, tmp_path):
        """Pass."""
        file_path = tmp_path / "test.csv"
        file_path.write_text(CSV_FILECONTENT_STR)
        config = {
            "user_id": "badwolf",
            "file_path": file_path,
        }
        cnx_added = apiobj.cnx.add(
            adapter_name=CSV_ADAPTER, adapter_node=DEFAULT_NODE, **config
        )

        assert isinstance(cnx_added["config"]["file_path"], dict)

        del_result = apiobj.cnx.delete_by_id(
            cnx_id=cnx_added["id"],
            adapter_name=CSV_ADAPTER,
            adapter_node=DEFAULT_NODE,
            delete_entities=True,
        )

        assert del_result == {"client_id": "badwolf"}

        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_id(
                cnx_id=cnx_added["id"],
                adapter_name=CSV_ADAPTER,
                adapter_node=DEFAULT_NODE,
            )

    def test_add_remove_path_notexists(self, apiobj, tmp_path):
        """Pass."""
        file_path = tmp_path / "badtest.csv"
        config = {
            "user_id": "badwolf",
            "file_path": file_path,
        }
        with pytest.raises(ConfigInvalidValue):
            apiobj.cnx.add(adapter_name=CSV_ADAPTER, adapter_node=DEFAULT_NODE, **config)

    def test_add_remove_stream(self, apiobj):
        """Pass."""
        config = {
            "user_id": "badwolf",
            "file_path": io.StringIO(CSV_FILECONTENT_STR),
        }
        cnx_added = apiobj.cnx.add(
            adapter_name=CSV_ADAPTER, adapter_node=DEFAULT_NODE, **config
        )

        assert isinstance(cnx_added["config"]["file_path"], dict)

        del_result = apiobj.cnx.delete_by_id(
            cnx_id=cnx_added["id"],
            adapter_name=CSV_ADAPTER,
            adapter_node=DEFAULT_NODE,
            delete_entities=True,
        )

        assert del_result == {"client_id": "badwolf"}

        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_id(
                cnx_id=cnx_added["id"],
                adapter_name=CSV_ADAPTER,
                adapter_node=DEFAULT_NODE,
            )

    def test_add_remove_error(self, apiobj, csv_file_path_broken):
        """Pass."""
        config = {
            "user_id": "badwolf",
            "file_path": csv_file_path_broken,
            # SANE_DEFAULTS handles these now:
            # "is_users": False,
            # "is_installed_sw": False,
            # "s3_use_ec2_attached_instance_profile": False,
        }
        with pytest.raises(CnxAddError) as exc:
            apiobj.cnx.add(adapter_name=CSV_ADAPTER, adapter_node=DEFAULT_NODE, **config)

        assert getattr(exc.value, "cnx_new", None)
        assert not hasattr(exc.value, "cnx_old")
        assert getattr(exc.value, "result", None)
        cnx_added = exc.value.cnx_new

        del_result = apiobj.cnx.delete_by_id(
            cnx_id=cnx_added["id"],
            adapter_name=CSV_ADAPTER,
            adapter_node=DEFAULT_NODE,
            delete_entities=True,
        )

        assert del_result == {"client_id": "badwolf"}

        with pytest.raises(NotFoundError):
            apiobj.cnx.get_by_id(
                cnx_id=cnx_added["id"],
                adapter_name=CSV_ADAPTER,
                adapter_node=DEFAULT_NODE,
                retry=2,
            )
