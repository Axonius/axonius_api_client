# -*- coding: utf-8 -*-
"""Test suite."""
import pytest


class TestInstancesPublic:
    @pytest.fixture(scope="class")
    def apiobj(self, api_instances):
        return api_instances

    def test_get(self, apiobj):
        data = apiobj.get()
        assert isinstance(data, dict)

        connection_data = data.pop("connection_data")
        assert isinstance(connection_data, dict)

        instances = data.pop("instances")
        assert isinstance(instances, list) and instances

        for instance in instances:
            assert isinstance(instance, dict)

        assert not data
