# -*- coding: utf-8 -*-
"""Test suite for assets."""

import copy

import pytest

from .test_callbacks import Callbacks


class TestCallbacksXml(Callbacks):
    @pytest.fixture(params=["api_devices"], scope="class")
    def apiobj(self, request):
        return request.getfixturevalue(request.param)

    @pytest.fixture(scope="class")
    def cbexport(self):
        return "xml"

    def test_standard(self, cbexport, apiobj, tmp_path):
        export_file = tmp_path / "badwolf.xml"
        rows = copy.deepcopy(apiobj.ORIGINAL_ROWS)
        cbobj = self.get_cbobj(
            apiobj=apiobj, cbexport=cbexport, getargs={"export_file": export_file}
        )
        cbobj.start()

        for row in rows:
            rows_ret = cbobj.process_row(row=copy.deepcopy(row))
            assert isinstance(rows_ret, list)
            assert len(rows_ret) == 1

        cbobj.stop()

        assert export_file.is_file()
