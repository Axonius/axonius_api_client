# -*- coding: utf-8 -*-
"""Test suite for assets."""

import copy

import pytest

from axonius_api_client.exceptions import ApiError

from .test_callbacks import Callbacks


class TestCallbacksXlsx(Callbacks):
    @pytest.fixture(params=["api_devices"], scope="class")
    def apiobj(self, request):
        return request.getfixturevalue(request.param)

    @pytest.fixture(scope="class")
    def cbexport(self):
        return "xlsx"

    def test_xlsx(self, cbexport, apiobj, tmp_path):
        export_file = tmp_path / "badwolf.xlsx"
        rows = copy.deepcopy(apiobj.ORIGINAL_ROWS)

        cbobj = self.get_cbobj(
            apiobj=apiobj, cbexport=cbexport, getargs={"export_file": export_file}
        )
        cbobj.start()

        for row in rows:
            row_id = row["internal_axon_id"]
            rows_ret = cbobj.process_row(row=copy.deepcopy(row))
            assert isinstance(rows_ret, list)
            assert len(rows_ret) == 1
            assert rows_ret[0] == {"internal_axon_id": row_id}

        cbobj.stop()

        assert export_file.is_file()

    def test_xlsx_added(self, cbexport, apiobj, tmp_path):
        export_file = tmp_path / "badwolf"
        rows = copy.deepcopy(apiobj.ORIGINAL_ROWS)

        cbobj = self.get_cbobj(
            apiobj=apiobj, cbexport=cbexport, getargs={"export_file": export_file}
        )
        cbobj.start()

        for row in rows:
            row_id = row["internal_axon_id"]
            rows_ret = cbobj.process_row(row=copy.deepcopy(row))
            assert isinstance(rows_ret, list)
            assert len(rows_ret) == 1
            assert rows_ret[0] == {"internal_axon_id": row_id}

        cbobj.stop()

        assert (tmp_path / "badwolf.xlsx").is_file()

    def test_fail_no_export_file(self, cbexport, apiobj, tmp_path):
        with pytest.raises(ApiError):
            cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs={})
            cbobj.start()
