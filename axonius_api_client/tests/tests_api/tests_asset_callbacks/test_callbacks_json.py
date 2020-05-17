# -*- coding: utf-8 -*-
"""Test suite for assets."""
import copy
import io
import json

import pytest

from .callbacks import Callbacks, load_test_data


class CallbacksJson(Callbacks):
    """Pass."""

    @pytest.fixture(scope="class")
    def cbexport(self):
        """Pass."""
        return "json"

    def test_row_as_is(self, cbexport, apiobj):
        """Pass."""
        io_fd = io.StringIO()

        getargs = {"export_fd": io_fd}

        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        cbobj.start()

        start_val = io_fd.getvalue().splitlines()[0]
        assert start_val == "["

        for row in copy.deepcopy(apiobj.TEST_DATA["cb_assets"][:200]):
            row_id = row["internal_axon_id"]
            rows_ret = cbobj.process_row(row=copy.deepcopy(row))
            assert len(rows_ret) == 1
            assert rows_ret[0] == {"internal_axon_id": row_id}
            assert f'    "internal_axon_id": "{row_id}",' in io_fd.getvalue()

        cbobj.stop()
        output = io_fd.getvalue()
        output_json = json.loads(output)
        assert isinstance(output_json, list)

        stop_val = output.splitlines()[-2:]
        assert "]" in stop_val

    def test_row_fully_loaded(self, cbexport, apiobj):
        """Pass."""
        io_fd = io.StringIO()

        getargs = {
            "export_fd": io_fd,
            "field_excludes": ["adapters"],
            "field_flatten": True,
            "field_titles": True,
            "field_join": True,
            "field_null": True,
            "report_adapters_missing": True,
            "export_schema": True,
        }
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        cbobj.start()

        start_val = io_fd.getvalue().splitlines()[0]
        assert start_val == "["

        for row in copy.deepcopy(apiobj.TEST_DATA["cb_assets"][:20]):
            row_id = row["internal_axon_id"]
            rows_ret = cbobj.process_row(row=copy.deepcopy(row))
            assert len(rows_ret) == 1
            assert rows_ret[0] == {"internal_axon_id": row_id}

        cbobj.stop()

        output = io_fd.getvalue()
        output_json = json.loads(output)
        assert isinstance(output_json, list)

        assert f'    "Aggregated: Asset Unique ID": "{row_id}",' in output
        assert '"schemas": [' in output
        stop_val = output.splitlines()[-2:]
        assert "]" in stop_val


class TestDevicesCallbacksJson(CallbacksJson):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        """Pass."""
        return load_test_data(apiobj=api_devices)


class TestUsersCallbacksJson(CallbacksJson):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        """Pass."""
        return load_test_data(apiobj=api_users)
