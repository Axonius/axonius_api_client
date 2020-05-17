# -*- coding: utf-8 -*-
"""Test suite for assets."""

import copy
import io

import pytest

from axonius_api_client.constants import AGG_ADAPTER_NAME
from axonius_api_client.exceptions import ApiError

from .callbacks import Callbacks, load_test_data


class CallbacksTable(Callbacks):
    """Pass."""

    @pytest.fixture(scope="class")
    def cbexport(self):
        """Pass."""
        return "table"

    def test_row_as_is(self, cbexport, apiobj):
        """Pass."""
        if not apiobj.TEST_DATA["has_complex"]:
            pytest.skip(f"No complex field found for {apiobj}")

        field_complex = apiobj.TEST_DATA["field_complex"]

        schema = apiobj.fields.get_field_schema(
            value=field_complex,
            schemas=apiobj.TEST_DATA["fields_map"][AGG_ADAPTER_NAME],
        )
        sub_titles = [x["column_title"] for x in schema["sub_fields"] if x["is_root"]]

        io_fd = io.StringIO()

        getargs = {"export_fd": io_fd}

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        cbobj.start()

        for row in copy.deepcopy(apiobj.TEST_DATA["cb_assets"][:200]):
            rows_ret = cbobj.process_row(row=copy.deepcopy(row))
            assert len(rows_ret) == 1
            # assert "Aggregated: Asset Unique ID" in rows_ret[0]
            # -> only if table_api_fields = True
            assert schema["name_qual"] not in rows_ret[0]
            for i in sub_titles:
                assert i in rows_ret[0]

        cbobj.stop()
        output = io_fd.getvalue()
        checklines = "\n".join(output.splitlines()[:3])
        for i in sub_titles:
            assert i in checklines

    def test_check_table_format(self, cbexport, apiobj):
        """Pass."""
        getargs = {}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        with pytest.raises(ApiError):
            cbobj.check_table_format("badwolf")

    def test_check_stop(self, cbexport, apiobj):
        """Pass."""
        getargs = {"table_max_rows": 10}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        cbobj.STATE["rows_processed_total"] = 10
        cbobj.check_stop()
        assert cbobj.STATE["stop_fetch"]
        assert cbobj.STATE["stop_msg"]


class TestDevicesCallbacksTable(CallbacksTable):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        """Pass."""
        return load_test_data(apiobj=api_devices)


class TestUsersCallbacksTable(CallbacksTable):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        """Pass."""
        return load_test_data(apiobj=api_users)
