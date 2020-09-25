# -*- coding: utf-8 -*-
"""Test suite."""
import pytest


class TestSystemInstances:
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_instances):
        """Pass."""
        return api_instances

    def test_get(self, apiobj):
        """Pass."""
        data = apiobj.get()
        assert isinstance(data, list)
