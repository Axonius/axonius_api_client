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
    """Pass."""

    def test_no_start(self, request):
        """Pass."""
        ax_url = get_url(request)

        c = Connect(url=ax_url, key=BAD_CRED, secret=BAD_CRED)

        assert "Not connected" in format(c)
        assert "Not connected" in repr(c)
        assert c._handler_file is None
        assert c._handler_con is None

    def test_no_start_logs(self, request):
        """Pass."""
        ax_url = get_url(request)

        c = Connect(
            url=ax_url, key=BAD_CRED, secret=BAD_CRED, log_console=True, log_file=True
        )

        assert "Not connected" in format(c)
        assert "Not connected" in repr(c)
        assert isinstance(c._handler_file, logging.Handler)
        assert isinstance(c._handler_con, logging.Handler)

    def test_start(self, request):
        """Pass."""
        ax_url = get_url(request)

        c = Connect(url=ax_url, certwarn=False, **get_key_creds(request))

        c.start()

        assert "Connected" in format(c)
        assert "Connected" in repr(c)

        format(c.system.settings_lifecycle)
        format(c.system.settings_gui)
        format(c.system.settings_core)
        format(c.system.users)
        format(c.system.roles)
        format(c.system.nodes)
        format(c.system.discover)
        format(c.system.meta)
        format(c.enforcements)
        format(c.users)
        format(c.devices)
        format(c.adapters)

    def test_invalid_creds(self, request):
        """Pass."""
        ax_url = get_url(request)

        c = Connect(url=ax_url, key=BAD_CRED, secret=BAD_CRED, certwarn=False)

        c._http.CONNECT_TIMEOUT = 1

        with pytest.raises(ConnectError) as exc:
            c.start()

        assert isinstance(exc.value.exc, InvalidCredentials)

    def test_connect_timeout(self):
        """Pass."""
        c = Connect(url="127.0.0.99", key=BAD_CRED, secret=BAD_CRED, certwarn=False)

        c._http.CONNECT_TIMEOUT = 1

        with pytest.raises(ConnectError) as exc:
            c.start()

        if IS_LINUX:
            assert isinstance(exc.value.exc, requests.ConnectionError)
        else:
            assert isinstance(exc.value.exc, requests.ConnectTimeout)

    def test_connect_error(self):
        """Pass."""
        c = Connect(
            url="https://127.0.0.1:3919", key=BAD_CRED, secret=BAD_CRED, certwarn=False
        )

        c._http.CONNECT_TIMEOUT = 1

        with pytest.raises(ConnectError) as exc:
            c.start()
        assert isinstance(exc.value.exc, requests.ConnectionError)

    def test_invalid_creds_nowrap(self, request):
        """Pass."""
        ax_url = get_url(request)

        c = Connect(
            url=ax_url, key=BAD_CRED, secret=BAD_CRED, certwarn=False, wraperror=False
        )

        c._http.CONNECT_TIMEOUT = 1

        with pytest.raises(InvalidCredentials):
            c.start()

    def test_other_exc(self, request):
        """Pass."""
        c = Connect(url="127.0.0.1", key=BAD_CRED, secret=BAD_CRED, certwarn=False)

        c._http.CONNECT_TIMEOUT = 1
        c._auth._creds = None

        with pytest.raises(ConnectError):
            c.start()

    def test_reason(self):
        """Pass."""
        exc = Exception("badwolf")

        reason = Connect._get_exc_reason(exc)

        assert format(reason) == "badwolf"
