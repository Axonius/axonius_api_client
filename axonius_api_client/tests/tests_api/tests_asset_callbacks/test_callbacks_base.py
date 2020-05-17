# -*- coding: utf-8 -*-
"""Test suite for assets."""
import copy

import pytest

from .callbacks import Callbacks, load_test_data


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

        rows = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][:5])

        for row in rows:
            rows_ret = cbobj.process_row(row=copy.deepcopy(row))
            for row_ret in rows_ret:
                assert row == row_ret
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

        rows = copy.deepcopy(apiobj.TEST_DATA["cb_assets"][:5])

        for row in rows:
            rows_ret = cbobj.process_row(row=copy.deepcopy(row))
            for row_ret in rows_ret:
                assert row != row_ret

        cbobj.stop()


class TestDevicesCallbacksBase(CallbacksBase):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        """Pass."""
        return load_test_data(apiobj=api_devices)


class TestUsersCallbacksBase(CallbacksBase):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        """Pass."""
        return load_test_data(apiobj=api_users)
