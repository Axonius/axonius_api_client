# -*- coding: utf-8 -*-
"""Test suite."""
import pytest


class SystemCentralCoreBase:
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_system):
        """Pass."""
        return api_system.central_core


class TestSystemCentralCorePrivate(SystemCentralCoreBase):
    """Pass."""

    def test_get(self, apiobj):
        """Pass."""
        data = apiobj._get()
        assert all([x is False for x in data.values()])


class TestSystemCentralCorePublic(SystemCentralCoreBase):
    """Pass."""

    def test_get(self, apiobj):
        """Pass."""
        data = apiobj.get()
        assert all([x is False for x in data.values()])
