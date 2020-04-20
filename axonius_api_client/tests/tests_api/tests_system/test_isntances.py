# -*- coding: utf-8 -*-
"""Test suite."""
import pytest


class TestSystemNodes:
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_system):
        """Pass."""
        return api_system.nodes

    def test_get(self, apiobj):
        """Pass."""
        data = apiobj.get()
        assert isinstance(data, list)
