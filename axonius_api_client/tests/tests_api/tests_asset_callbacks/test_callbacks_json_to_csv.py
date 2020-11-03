# -*- coding: utf-8 -*-
"""Test suite for assets."""
import io

import pytest

from ...utils import get_rows_exist
from .test_callbacks import Callbacks, Exports


class TestCallbacksJsonToCsv(Callbacks, Exports):
    @pytest.fixture(params=["api_devices", "api_users"])
    def apiobj(self, request):
        return request.getfixturevalue(request.param)

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
            getargs={"export_fd": io_fd, "export_fd_close": False},
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
