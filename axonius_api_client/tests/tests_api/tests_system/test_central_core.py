# -*- coding: utf-8 -*-
"""Test suite."""
import pytest


class SystemCentralCoreBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_system):
        return api_system.central_core


class TestSystemCentralCorePrivate(SystemCentralCoreBase):
    def test_get(self, apiobj):
        data = apiobj._get()
        assert all([x is False for x in data.values()])


class TestSystemCentralCorePublic(SystemCentralCoreBase):
    def test_get(self, apiobj):
        data = apiobj.get()
        assert all([x is False for x in data.values()])
