# -*- coding: utf-8 -*-
"""Test suite for assets."""
import copy
import io

import pytest
from axonius_api_client.constants import AGG_ADAPTER_NAME

from .callbacks import Callbacks, load_test_data


class CallbacksCsv(Callbacks):
    """Pass."""

    @pytest.fixture(scope="class")
    def cbexport(self):
        """Pass."""
        return "csv"

    def test_row_as_is(self, cbexport, apiobj):
        """Pass."""
        field_complex = apiobj.TEST_DATA["field_complex"]
        if field_complex is None:
            pytest.skip(f"No complex field found for {apiobj}")

        schema = apiobj.fields.get_field_schema(
            value=field_complex,
            schemas=apiobj.TEST_DATA["fields_map"][AGG_ADAPTER_NAME],
        )
        sub_titles = [x["column_title"] for x in schema["sub_fields"] if x["is_root"]]

        io_fd = io.StringIO()

        getargs = {"export_fd": io_fd}

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        cbobj.start()

        start_val = io_fd.getvalue().splitlines()[0]
        for i in sub_titles:
            assert f'"{i}"' in start_val

        for row in copy.deepcopy(apiobj.TEST_DATA["cb_assets"][:200]):
            row_id = row["internal_axon_id"]
            rows_ret = cbobj.row(row=copy.deepcopy(row))
            assert len(rows_ret) == 1
            assert rows_ret[0] == {"internal_axon_id": row_id}

        cbobj.stop()
        output = io_fd.getvalue()
        assert output.endswith("\n\n")


class TestDevicesCallbacksCsv(CallbacksCsv):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        """Pass."""
        return load_test_data(apiobj=api_devices)


class TestUsersCallbacksCsv(CallbacksCsv):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        """Pass."""
        return load_test_data(apiobj=api_users)
