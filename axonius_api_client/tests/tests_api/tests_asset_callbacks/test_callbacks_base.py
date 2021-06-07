# -*- coding: utf-8 -*-
"""Test suite for assets."""
import copy

import pytest

from ...utils import get_rows_exist
from .test_callbacks import Callbacks


class TestCallbacksBase(Callbacks):
    @pytest.fixture(params=["devices", "users"])
    def apiobj(self, api_client, request):
        return getattr(api_client, request.param)

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

    # def test_fields_selected_include_details(self, cbexport, apiobj, caplog):
    #     getargs = {
    #         "report_adapters_missing": True,
    #     }
    #     store = {
    #         "include_details": True,
    #         "fields": [apiobj.FIELD_SIMPLE],
    #     }
    #     cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs, store=store)
    #     cbobj.start()

    #     rows = get_rows_exist(
    #         apiobj=apiobj,
    #         fields=[apiobj.FIELD_SIMPLE],
    #         fields_default=False,
    #         max_rows=5,
    #         include_details=True,
    #         fields_null=True,
    #     )
    #     exp = [
    #         *apiobj.FIELDS_API,
    #         *[
    #             apiobj.FIELDS_DETAIL_TMPL.format(x)
    #             for x in apiobj.FIELDS_API
    #             if x != apiobj.FIELD_ADAPTERS
    #         ],
    #         apiobj.FIELD_SIMPLE,
    #         apiobj.FIELDS_DETAIL_TMPL.format(apiobj.FIELD_SIMPLE),
    #         *apiobj.FIELDS_DETAILS,
    #         *[apiobj.FIELDS_DETAIL_TMPL.format(x) for x in apiobj.FIELDS_DETAILS],
    #     ]
    #     assert sorted(cbobj.fields_selected) == sorted(exp)
    #     import pdb

    #     pdb.set_trace()
    #     for row in rows:
    #         for f in exp:
    #             if f != apiobj.FIELD_TAGS:
    #                 assert f in row
    #             row.pop(f, None)
    #         assert not row

    #     cbobj.stop()
