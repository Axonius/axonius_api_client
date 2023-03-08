# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

from axonius_api_client.tools import json_load

from ...tests_api.tests_system.test_data_scopes import DataScopeFixtures, FixtureData


class Meta:
    """Pass."""

    name = "badwolf CLI"
    name_update = f"{name} UPDATED"
    names = [name, name_update]
    fixture_data = FixtureData


class DataScopesBase(DataScopeFixtures):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_data_scopes):
        """Pass."""
        if not api_data_scopes.is_feature_enabled:
            pytest.skip("Data Scopes Feature Flag not enabled")

        return api_data_scopes

    def check_result(self, result, exit_codes=[0]):
        """Pass."""
        assert result.stdout
        assert result.stderr
        assert result.exit_code in exit_codes

        data = json_load(result.stdout)
        assert isinstance(data, (list, dict))
        if isinstance(data, list):
            for i in data:
                assert isinstance(i, dict)
        return data
