# -*- coding: utf-8 -*-
"""Test suite for assets."""
import copy
import io

import pytest

from ...utils import get_rows_exist, get_schema
from .test_callbacks import Callbacks, Exports


class TestCallbacksCsv(Callbacks, Exports):
    @pytest.fixture(params=["api_devices", "api_users"])
    def apiobj(self, request):
        return request.getfixturevalue(request.param)

    @pytest.fixture(scope="class")
    def cbexport(self):
        return "csv"

    def test_row_as_is(self, cbexport, apiobj):
        field_complex = apiobj.FIELD_COMPLEX
        sub_columns = [
            x["column_title"]
            for x in get_schema(apiobj=apiobj, field=field_complex, key="sub_fields")
            if x["is_root"]
        ]
        original_rows = get_rows_exist(apiobj=apiobj, fields=field_complex, max_rows=5)

        io_fd = io.StringIO()

        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields": [field_complex]},
            getargs={"export_fd": io_fd, "export_fd_close": False},
        )
        cbobj.start()

        assert isinstance(cbobj.final_schemas, list)
        assert cbobj.final_schemas
        for x in cbobj.final_schemas:
            assert isinstance(x, dict)

        for row in original_rows:
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

    def test_row_no_titles(self, cbexport, apiobj):
        rows = get_rows_exist(apiobj=apiobj, max_rows=5)

        io_fd = io.StringIO()
        cbobj = self.get_cbobj(
            apiobj=apiobj,
            cbexport=cbexport,
            store={"fields": apiobj.fields_default},
            getargs={"export_fd": io_fd, "field_titles": False, "export_fd_close": False},
        )
        cbobj.start()
        assert cbobj.GETARGS["field_titles"] is False

        for row in rows:
            cbobj.process_row(row=copy.deepcopy(row))

        start_val = io_fd.getvalue().splitlines()[0]
        for i in cbobj.final_columns:
            assert f'"{i}"' in start_val

        cbobj.stop()
        output = io_fd.getvalue()
        assert output.endswith("\n\n")
