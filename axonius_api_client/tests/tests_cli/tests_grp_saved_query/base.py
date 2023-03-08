# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

from axonius_api_client.exceptions import NotFoundError
from axonius_api_client.tools import json_load


class FixtureData:
    """Pass."""

    delete_name = "badwolf cli delete"
    add_name = "badwolf cli add"
    tags = [f"badwolf cli tag {x}" for x in range(3)]


class SavedQueryFixtures:
    """Pass."""

    def _cleanup(self, apiobj, value):
        try:
            sq = apiobj.saved_query.get_by_multi(sq=value, as_dataclass=True)
        except NotFoundError:
            pass
        else:
            apiobj.saved_query.delete(rows=sq, as_dataclass=True, refetch=False)

    @pytest.fixture(scope="function")
    def sq_added(self, apiobj):
        """Pass."""
        self._cleanup(apiobj=apiobj, value=FixtureData.delete_name)

        sq = apiobj.saved_query.add(
            name=FixtureData.delete_name, tags=FixtureData.tags, as_dataclass=True
        )

        yield sq

        self._cleanup(apiobj=apiobj, value=FixtureData.delete_name)

    @pytest.fixture(scope="class")
    def sq_get(self, apiobj):
        """Pass."""
        return apiobj.saved_query.get(as_dataclass=True, row_stop=1, page_size=1)[0]

    @pytest.fixture(scope="class")
    def sq_tags(self, apiobj):
        """Pass."""
        return apiobj.saved_query.get_tags()

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


class GrpSavedQueryDevices(SavedQueryFixtures):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_client):
        """Pass."""
        return api_client.devices


class GrpSavedQueryUsers(SavedQueryFixtures):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_client):
        """Pass."""
        return api_client.users
