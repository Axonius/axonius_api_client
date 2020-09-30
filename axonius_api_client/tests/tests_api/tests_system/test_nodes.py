# -*- coding: utf-8 -*-
"""Test suite."""
import pytest


class TestSystemInstances:
    @pytest.fixture(scope="class")
    def apiobj(self, api_instances):
        return api_instances

    def test_get(self, apiobj):
        data = apiobj.get()
        assert isinstance(data, list)
