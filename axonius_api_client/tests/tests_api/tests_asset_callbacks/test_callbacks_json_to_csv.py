# -*- coding: utf-8 -*-
"""Test suite for assets."""
import io

import pytest

from ...utils import get_rows_exist
from .callbacks import Callbacks


class CallbacksJsonToCsv(Callbacks):
    @pytest.fixture(scope="class")
    def cbexport(self):
        return "json_to_csv"

    def test_row_as_is(self, cbexport, apiobj):
        rows = get_rows_exist(apiobj=apiobj, max_rows=5)

        io_fd = io.StringIO()
        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields": apiobj.fields_default},
            getargs={"export_fd": io_fd},
        )
        cbobj.start()

        for row in rows:
            _id = row[apiobj.FIELD_AXON_ID]
            new_rows = cbobj.process_row(row=row)
            assert new_rows == [{apiobj.FIELD_AXON_ID: _id}]

        cbobj.stop()

        start_val = io_fd.getvalue().splitlines()[0]
        for i in cbobj.final_columns:
            assert f'"{i}"' in start_val


class TestDevicesCallbacksJsonToCsv(CallbacksJsonToCsv):
    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        return api_devices


class TestUsersCallbacksJsonToCsv(CallbacksJsonToCsv):
    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        return api_users
