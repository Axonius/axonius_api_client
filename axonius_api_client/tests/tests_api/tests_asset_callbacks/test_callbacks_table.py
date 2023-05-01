# -*- coding: utf-8 -*-
"""Test suite for assets."""

import copy
import io

import pytest

from axonius_api_client.exceptions import ApiError, StopFetch

from ...utils import get_schema
from .test_callbacks import Exports


class TestCallbacksTable(Exports):
    @pytest.fixture(params=["api_devices"], scope="class")
    def apiobj(self, request):
        return request.getfixturevalue(request.param)

    @pytest.fixture(scope="class")
    def cbexport(self):
        return "table"

    def test_row_as_is(self, cbexport, apiobj):
        field_complex = apiobj.FIELD_COMPLEX
        sub_columns = [
            x["column_title"]
            for x in get_schema(apiobj=apiobj, field=field_complex, key="sub_fields")
            if x["is_root"]
        ]
        original_rows = copy.deepcopy(apiobj.COMPLEX_ROWS)

        io_fd = io.StringIO()

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields_parsed": [field_complex]},
            getargs={"export_fd": io_fd, "export_fd_close": False, "table_max_rows": 4},
        )
        cbobj.start()

        for idx, row in enumerate(copy.deepcopy(original_rows)):
            try:
                rows_ret = cbobj.process_row(row=copy.deepcopy(row))
            except StopFetch:
                if not idx >= 3:
                    raise
            assert len(rows_ret) == 1
            # assert "Aggregated: Asset Unique ID" in rows_ret[0]
            # -> only if table_api_fields = True
            assert field_complex not in rows_ret[0]
            for i in sub_columns:
                assert i in rows_ret[0]

        cbobj.stop()
        output = io_fd.getvalue()
        checklines = "\n".join(output.splitlines()[:3])
        for i in sub_columns:
            assert i in checklines

    def test_check_table_format(self, cbexport, apiobj):
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport)
        with pytest.raises(ApiError):
            cbobj.check_table_format("badwolf")

    def test_check_stop(self, cbexport, apiobj):
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={"table_max_rows": 10})
        cbobj.STATE["rows_processed_total"] = 10
        with pytest.raises(StopFetch):
            cbobj.check_stop()
        assert cbobj.STATE["stop_fetch"]
        assert cbobj.STATE["stop_msg"]
