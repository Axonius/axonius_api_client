# -*- coding: utf-8 -*-
"""Test suite."""

import datetime

import pytest
from axonius_api_client.api.system.remote_support import RemoteData


class RemoteSupportBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_remote_support):
        return api_remote_support


class TestRemoteSupportPrivate(RemoteSupportBase):
    def test_get(self, apiobj):
        data = apiobj._get()
        assert isinstance(data, dict)

        analytics = data.pop("analytics")
        assert isinstance(analytics, bool)

        modified = data.pop("_id")
        assert isinstance(modified, str)

        provision = data.pop("provision")
        assert isinstance(provision, bool)

        timeout = data.pop("timeout")
        assert isinstance(timeout, (str, type(None)))

        troubleshooting = data.pop("troubleshooting")
        assert isinstance(troubleshooting, bool)

        dtype = data.pop("type")
        assert dtype == "maintenance"

        assert not data

    def test_start_stop_temp(self, apiobj):
        apiobj._update({"provision": False})

        start_data = apiobj._start_temp(hours=24)
        assert isinstance(start_data, dict)

        timeout = start_data.pop("timeout")
        assert isinstance(timeout, str)

        assert not start_data

        start_check = apiobj._get()
        assert start_check["provision"] is False
        assert start_check["timeout"] and isinstance(start_check["timeout"], str)

        stop_data = apiobj._stop_temp()
        assert isinstance(stop_data, str) and not stop_data

        stop_check = apiobj._get()
        assert stop_check["provision"] is False
        assert stop_check["timeout"] is None

        apiobj._update({"provision": True})


class TestRemoteSupportPublic(RemoteSupportBase):
    def test_get(self, apiobj):
        data = apiobj.get()
        assert isinstance(data, RemoteData)

        assert isinstance(data.enabled_permanently, bool)
        assert isinstance(data.enabled, bool)
        assert isinstance(data.enabled_temporarily, bool)
        assert isinstance(data.temporary_expiry_date, (datetime.datetime, type(None)))
        assert isinstance(data.temporary_expires_in_hours, (float, type(None)))
        assert isinstance(data.analytics_enabled, bool)
        assert isinstance(data.remote_access_enabled, bool)
        assert str(data)
        assert repr(data)

        assert isinstance(data.to_dict(), dict)
        assert isinstance(data.to_str_properties(), list)

    def test_configure_remote_access(self, apiobj):
        data_off = apiobj.configure_remote_access(enable=False)
        assert isinstance(data_off, RemoteData)
        assert data_off.remote_access_enabled is False

        data_on = apiobj.configure_remote_access(enable=True)
        assert isinstance(data_on, RemoteData)
        assert data_on.remote_access_enabled is True

    def test_configure_analytics(self, apiobj):
        data_off = apiobj.configure_analytics(enable=False)
        assert isinstance(data_off, RemoteData)
        assert data_off.analytics_enabled is False

        data_on = apiobj.configure_analytics(enable=True)
        assert isinstance(data_on, RemoteData)
        assert data_on.analytics_enabled is True

    def test_configure_start_stop(self, apiobj):
        stop = apiobj.configure(enable=False)
        assert isinstance(stop, RemoteData)
        assert stop.enabled is False
        assert stop.enabled_temporarily is False
        assert stop.enabled_permanently is False

        start = apiobj.configure(enable=True)
        assert isinstance(start, RemoteData)
        assert start.enabled is True
        assert start.enabled_temporarily is False
        assert start.enabled_permanently is True

    def test_configure_start_stop_temp(self, apiobj):
        start_temp = apiobj.configure(enable=True, temp_hours=24)
        assert isinstance(start_temp, RemoteData)
        assert start_temp.enabled is True
        assert start_temp.enabled_temporarily is True
        assert start_temp.enabled_permanently is False
        assert isinstance(start_temp.temporary_expiry_date, datetime.datetime)
        assert isinstance(start_temp.temporary_expires_in_hours, float)

        stop = apiobj.configure(enable=False)
        assert isinstance(stop, RemoteData)
        assert stop.enabled is False
        assert stop.enabled_temporarily is False
        assert stop.enabled_permanently is False
        assert stop.temporary_expiry_date is None
        assert stop.temporary_expires_in_hours is None

        start = apiobj.configure(enable=True)
        assert isinstance(start, RemoteData)
        assert start.enabled is True
        assert start.enabled_temporarily is False
        assert start.enabled_permanently is True
