# -*- coding: utf-8 -*-
"""Test suite for assets."""
import copy

import pytest

from ...utils import get_rows_exist
from .callbacks import Callbacks


class CallbacksBase(Callbacks):
    """Pass."""

    @pytest.fixture(scope="class")
    def cbexport(self):
        """Pass."""
        return "base"

    def test_row_as_is(self, cbexport, apiobj, caplog):
        """Pass."""
        getargs = {}
        cbobj = self.get_cbobj(apiobj=apiobj, cbexport=cbexport, getargs=getargs)
        cbobj.start()

        rows_orig = get_rows_exist(apiobj=apiobj, max_rows=5, first=False)
        rows = copy.deepcopy(rows_orig)
        rows_proc = []
        for row in rows:
            rows_proc += cbobj.process_row(row=row)

        assert rows_proc == rows_orig
        cbobj.stop()

    def test_row_fully_loaded(self, cbexport, apiobj, caplog):
        """Pass."""
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

        rows_orig = get_rows_exist(apiobj=apiobj, max_rows=5, first=False)
        rows = copy.deepcopy(rows_orig)
        rows_proc = []
        for row in rows:
            rows_proc += cbobj.process_row(row=row)

        assert rows_proc != rows_orig
        cbobj.stop()


class TestDevicesCallbacksBase(CallbacksBase):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        """Pass."""
        return api_devices


class TestUsersCallbacksBase(CallbacksBase):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        """Pass."""
        return api_users
