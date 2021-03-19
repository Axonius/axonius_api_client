# -*- coding: utf-8 -*-
"""Test suite for assets."""

import pytest


class TestCallbacksXml:
    @pytest.fixture(params=["devices", "_users"])
    def apiobj(self, api_client, request):
        return getattr(api_client, request.param)
        # return request.getfixturevalue(request.param)

    @pytest.fixture(scope="class")
    def cbexport(self):
        return "xml"

    def test_standard(self, cbexport, apiobj, tmp_path):
        export_file = tmp_path / "badwolf.xml"
        rows = apiobj.get(max_rows=1, export=cbexport, export_file=export_file)
        assert isinstance(rows, list)
        assert export_file.is_file()
