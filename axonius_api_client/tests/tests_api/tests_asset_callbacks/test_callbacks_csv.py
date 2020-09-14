# -*- coding: utf-8 -*-
"""Test suite for assets."""
import copy
import io

import pytest
from axonius_api_client.constants import AGG_ADAPTER_NAME

from .callbacks import Callbacks


class CallbacksCsv(Callbacks):
    """Pass."""

    @pytest.fixture(scope="class")
    def cbexport(self):
        """Pass."""
        return "csv"

    def test_row_as_is(self, cbexport, apiobj):
        """Pass."""
        if not apiobj.TEST_DATA["has_complex"]:
            pytest.skip(f"No complex field found for {apiobj}")

        field_complex = apiobj.TEST_DATA["field_complex"]

        schema = apiobj.fields.get_field_schema(
            value=field_complex, schemas=apiobj.fields.get()[AGG_ADAPTER_NAME],
        )
        sub_columns = [x["column_title"] for x in schema["sub_fields"] if x["is_root"]]

        io_fd = io.StringIO()

        getargs = {"export_fd": io_fd}

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        cbobj.start()

        assert isinstance(cbobj.final_schemas, list)
        assert cbobj.final_schemas
        for x in cbobj.final_schemas:
            assert isinstance(x, dict)

        for row in copy.deepcopy(apiobj.TEST_DATA["cb_assets"][:200]):
            row_id = row["internal_axon_id"]
            rows_ret = cbobj.process_row(row=copy.deepcopy(row))
            assert len(rows_ret) == 1
            assert rows_ret[0] == {"internal_axon_id": row_id}

        start_val = io_fd.getvalue().splitlines()[0]
        for i in sub_columns:
            assert f'"{i}"' in start_val

        cbobj.stop()
        output = io_fd.getvalue()
        assert output.endswith("\n\n")


class TestDevicesCallbacksCsv(CallbacksCsv):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        """Pass."""
        return api_devices


class TestUsersCallbacksCsv(CallbacksCsv):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        """Pass."""
        return api_users
