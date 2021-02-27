# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import logging

import pytest

from axonius_api_client.connect import Connect
from axonius_api_client.exceptions import ConnectError, InvalidCredentials
from axonius_api_client.http import requests

from ..utils import IS_LINUX, get_key_creds, get_url

BAD_CRED = "tardis"


class TestConnect:
    def test_no_start(self, request):
        ax_url = get_url(request)

        c = Connect(url=ax_url, key=BAD_CRED, secret=BAD_CRED)

        assert "Not connected" in format(c)
        assert "Not connected" in repr(c)
        assert c.HANDLER_FILE is None
        assert c.HANDLER_CON is None

    def test_no_start_logs(self, request):
        ax_url = get_url(request)

        c = Connect(url=ax_url, key=BAD_CRED, secret=BAD_CRED, log_console=True, log_file=True)

        assert "Not connected" in format(c)
        assert "Not connected" in repr(c)
        assert isinstance(c.HANDLER_FILE, logging.Handler)
        assert isinstance(c.HANDLER_CON, logging.Handler)

    def test_start(self, request):
        ax_url = get_url(request)

        c = Connect(url=ax_url, certwarn=False, **get_key_creds(request))

        c.start()

        assert "Connected" in format(c)
        assert "Connected" in repr(c)

        props = [
            "activity_logs",
            "adapters",
            "dashboard",
            "devices",
            "enforcements",
            "instances",
            "meta",
            "remote_support",
            "settings_global",
            "settings_gui",
            "settings_ip",
            "settings_lifecycle",
            "signup",
            "system_roles",
            "system_users",
            "users",
        ]
        for prop in props:
            prop_attr = getattr(c, prop)
            assert format(prop_attr)
            assert repr(prop_attr)

    def test_invalid_creds(self, request):
        ax_url = get_url(request)

        c = Connect(url=ax_url, key=BAD_CRED, secret=BAD_CRED, certwarn=False)

        c.HTTP.CONNECT_TIMEOUT = 1

        with pytest.raises(ConnectError) as exc:
            c.start()

        assert isinstance(exc.value.exc, InvalidCredentials)

    def test_connect_timeout(self):
        c = Connect(url="127.0.0.99", key=BAD_CRED, secret=BAD_CRED, certwarn=False)

        c.HTTP.CONNECT_TIMEOUT = 1

        with pytest.raises(ConnectError) as exc:
            c.start()

        if IS_LINUX:
            assert isinstance(exc.value.exc, requests.ConnectionError)
        else:
            assert isinstance(exc.value.exc, requests.ConnectTimeout)

    def test_connect_error(self):
        c = Connect(url="https://127.0.0.1:3919", key=BAD_CRED, secret=BAD_CRED, certwarn=False)

        c.HTTP.CONNECT_TIMEOUT = 1

        with pytest.raises(ConnectError) as exc:
            c.start()
        assert isinstance(exc.value.exc, requests.ConnectionError)

    def test_invalid_creds_nowrap(self, request):
        ax_url = get_url(request)

        c = Connect(url=ax_url, key=BAD_CRED, secret=BAD_CRED, certwarn=False, wraperror=False)

        c.HTTP.CONNECT_TIMEOUT = 1

        with pytest.raises(InvalidCredentials):
            c.start()

    def test_other_exc(self, request):
        c = Connect(url="127.0.0.1", key=BAD_CRED, secret=BAD_CRED, certwarn=False)

        c.HTTP.CONNECT_TIMEOUT = 1
        c.AUTH._creds = None

        with pytest.raises(ConnectError):
            c.start()

    def test_reason(self):
        exc = Exception("badwolf")

        reason = Connect._get_exc_reason(exc)

        assert format(reason) == "badwolf"
