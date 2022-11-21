# -*- coding: utf-8 -*-
"""Test suite."""

import datetime

import pytest

from axonius_api_client.api import json_api
from axonius_api_client.exceptions import ApiError


class ActivityLogsBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_activity_logs):
        return api_activity_logs


class TestActivityLogsPrivate(ActivityLogsBase):
    def test_get(self, apiobj):
        data = apiobj._get()
        assert isinstance(data, list)
        for row in data:
            assert isinstance(row, json_api.audit_logs.AuditLog)


class TestActivityLogsPublic(ActivityLogsBase):
    def test_get(self, apiobj):
        data = apiobj.get()
        assert isinstance(data, list)
        for row in data:
            assert isinstance(row, json_api.audit_logs.AuditLog)
            assert str(row)
            assert repr(row)
            assert isinstance(row.action, str)
            assert isinstance(row.category, str)
            assert isinstance(row.date, datetime.datetime)
            assert isinstance(row.user, str)
            assert isinstance(row.hours_ago, float)
            assert row.within_last_hours() is True
            assert row.within_dates() is True
            assert row.property_searches() is True
            assert row.within_dates(start="1999-01-01 11:00am", end="1999-01-01 11:00pm") is False
            assert row.property_searches(category=".*") is True
            assert row.property_searches(category=["badwolf"], action=["badwolf"]) is False
            with pytest.raises(ApiError):
                row.property_searches(badwolf="x")

    def test_get_within_last_hours(self, apiobj):
        data = apiobj.get(within_last_hours=12)
        assert isinstance(data, list)
        for row in data:
            assert row.hours_ago <= 13

        data = apiobj.get(within_last_hours=-1)
        assert isinstance(data, list)
        assert not data
