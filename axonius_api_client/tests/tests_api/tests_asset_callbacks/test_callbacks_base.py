# -*- coding: utf-8 -*-
"""Test suite for assets."""
import copy

import pytest

from ...utils import get_rows_exist
from .test_callbacks import Callbacks


class TestCallbacksBase(Callbacks):
    @pytest.fixture(params=["api_devices", "api_users"])
    def apiobj(self, request):
        return request.getfixturevalue(request.param)

    @pytest.fixture(scope="class")
    def cbexport(self):
        return "base"

    def test_row_as_is(self, cbexport, apiobj, caplog):
        getargs = {}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        cbobj.start()

        rows_orig = get_rows_exist(apiobj=apiobj, max_rows=5)
        rows = copy.deepcopy(rows_orig)
        rows_proc = []
        for row in rows:
            rows_proc += cbobj.process_row(row=row)

        assert rows_proc == rows_orig
        cbobj.stop()

    def test_row_fully_loaded(self, cbexport, apiobj, caplog):
        getargs = {
            "field_excludes": ["adapters"],
            "field_flatten": True,
            "field_titles": True,
            "field_join": True,
            "field_null": True,
            "report_adapters_missing": True,
        }
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        cbobj.start()

        rows_orig = get_rows_exist(apiobj=apiobj, max_rows=5)
        rows = copy.deepcopy(rows_orig)
        rows_proc = []
        for row in rows:
            rows_proc += cbobj.process_row(row=row)

        assert rows_proc != rows_orig
        cbobj.stop()
