# -*- coding: utf-8 -*-
"""Test suite."""

import datetime

from axonius_api_client.api import json_api


class RemoteSupportBase:
    """Pass."""


class TestRemoteSupportPrivate(RemoteSupportBase):
    def test_get(self, api_client):
        data = api_client.remote_support._get()
        assert isinstance(data, json_api.remote_support.RemoteSupport)

    def test_start_stop_temp(self, api_client):
        api_client.remote_support._update_permanent(provision=False)

        start_data = api_client.remote_support._start_temporary(hours=24)
        assert isinstance(start_data, json_api.remote_support.UpdateTemporaryResponse)
        assert isinstance(start_data.timeout, str)

        start_check = api_client.remote_support._get()
        assert start_check.provision is False
        assert start_check.timeout and isinstance(start_check.timeout, datetime.datetime)

        stop_data = api_client.remote_support._stop_temporary()
        assert isinstance(stop_data, str) and not stop_data

        stop_check = api_client.remote_support._get()
        assert stop_check.provision is False
        assert stop_check.timeout is None

        api_client.remote_support._update_permanent(provision=True)


class TestRemoteSupportPublic(RemoteSupportBase):
    def test_get(self, api_client):
        data = api_client.remote_support.get()
        assert isinstance(data, json_api.remote_support.RemoteSupport)

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
        assert isinstance(data._to_str_properties(), list) and data._to_str_properties()

    def test_configure_remote_access(self, api_client):
        data_off = api_client.remote_support.configure_remote_access(enable=False)
        assert isinstance(data_off, json_api.remote_support.RemoteSupport)
        assert data_off.remote_access_enabled is False

        data_on = api_client.remote_support.configure_remote_access(enable=True)
        assert isinstance(data_on, json_api.remote_support.RemoteSupport)
        assert data_on.remote_access_enabled is True

    def test_configure_analytics(self, api_client):
        data_off = api_client.remote_support.configure_analytics(enable=False)
        assert isinstance(data_off, json_api.remote_support.RemoteSupport)
        assert data_off.analytics_enabled is False

        data_on = api_client.remote_support.configure_analytics(enable=True)
        assert isinstance(data_on, json_api.remote_support.RemoteSupport)
        assert data_on.analytics_enabled is True

    def test_configure_start_stop(self, api_client):
        stop = api_client.remote_support.configure(enable=False)
        assert isinstance(stop, json_api.remote_support.RemoteSupport)
        assert stop.enabled is False
        assert stop.enabled_temporarily is False
        assert stop.enabled_permanently is False

        start = api_client.remote_support.configure(enable=True)
        assert isinstance(start, json_api.remote_support.RemoteSupport)
        assert start.enabled is True
        assert start.enabled_temporarily is False
        assert start.enabled_permanently is True

    def test_configure_start_stop_temp(self, api_client):
        start_temp = api_client.remote_support.configure(enable=True, temp_hours=24)
        assert isinstance(start_temp, json_api.remote_support.RemoteSupport)
        assert start_temp.enabled is True
        assert start_temp.enabled_temporarily is True
        assert start_temp.enabled_permanently is False
        assert isinstance(start_temp.temporary_expiry_date, datetime.datetime)
        assert isinstance(start_temp.temporary_expires_in_hours, float)

        stop = api_client.remote_support.configure(enable=False)
        assert isinstance(stop, json_api.remote_support.RemoteSupport)
        assert stop.enabled is False
        assert stop.enabled_temporarily is False
        assert stop.enabled_permanently is False
        assert stop.temporary_expiry_date is None
        assert stop.temporary_expires_in_hours is None

        start = api_client.remote_support.configure(enable=True)
        assert isinstance(start, json_api.remote_support.RemoteSupport)
        assert start.enabled is True
        assert start.enabled_temporarily is False
        assert start.enabled_permanently is True
