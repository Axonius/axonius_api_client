# -*- coding: utf-8 -*-
"""Test suite for assets."""

import pytest

from axonius_api_client.exceptions import ApiError


class TestCallbacksXlsx:
    @pytest.fixture(params=["api_devices", "api_users"])
    def apiobj(self, request):
        return request.getfixturevalue(request.param)

    @pytest.fixture(scope="class")
    def cbexport(self):
        return "xlsx"

    def test_xlsx(self, cbexport, apiobj, tmp_path):
        export_file = tmp_path / "badwolf.xlsx"
        rows = apiobj.get(max_rows=1, export=cbexport, export_file=export_file)
        for row in rows:
            assert row.pop(apiobj.FIELD_AXON_ID)
            assert not row
        assert export_file.is_file()

    def test_xlsx_added(self, cbexport, apiobj, tmp_path):
        export_file = tmp_path / "badwolf"
        rows = apiobj.get(max_rows=1, export=cbexport, export_file=export_file)
        for row in rows:
            assert row.pop(apiobj.FIELD_AXON_ID)
            assert not row
        assert (tmp_path / "badwolf.xlsx").is_file()

    def test_fail_no_export_file(self, cbexport, apiobj, tmp_path):
        with pytest.raises(ApiError):
            apiobj.get(max_rows=1, export=cbexport)
