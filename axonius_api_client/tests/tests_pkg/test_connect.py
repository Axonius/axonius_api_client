# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import pytest

import axonius_api_client as axonapi
from axonius_api_client import connect, exceptions

from .. import utils

BAD_CRED = "tardis"


class TestConnect(object):
    """Pass."""

    def test_no_start(self, request):
        """Pass."""
        ax_url = utils.get_url(request)

        c = connect.Connect(url=ax_url, key=BAD_CRED, secret=BAD_CRED)

        assert "Not connected" in format(c)
        assert "Not connected" in repr(c)
        assert c._handler_file is None
        assert c._handler_con is None

    def test_no_start_logs(self, request):
        """Pass."""
        ax_url = utils.get_url(request)

        c = connect.Connect(
            url=ax_url, key=BAD_CRED, secret=BAD_CRED, log_console=True, log_file=True
        )

        assert "Not connected" in format(c)
        assert "Not connected" in repr(c)
        assert isinstance(c._handler_file, logging.Handler)
        assert isinstance(c._handler_con, logging.Handler)

    def test_start(self, request):
        """Pass."""
        ax_url = utils.get_url(request)

        c = connect.Connect(url=ax_url, certwarn=False, **utils.get_key_creds(request))

        c.start()

        assert "Connected" in format(c)
        assert "Connected" in repr(c)
        with pytest.warns(exceptions.BetaWarning):
            format(c.enforcements)
        format(c.users)
        format(c.devices)
        format(c.adapters)

    def test_invalid_creds(self, request):
        """Pass."""
        ax_url = utils.get_url(request)

        c = connect.Connect(url=ax_url, key=BAD_CRED, secret=BAD_CRED, certwarn=False)

        c._http._CONNECT_TIMEOUT = 1

        with pytest.raises(exceptions.ConnectError) as exc:
            c.start()

        assert isinstance(exc.value.exc, exceptions.InvalidCredentials)

    def test_connect_timeout(self):
        """Pass."""
        c = connect.Connect(
            url="127.0.0.99", key=BAD_CRED, secret=BAD_CRED, certwarn=False
        )

        c._http._CONNECT_TIMEOUT = 1

        with pytest.raises(exceptions.ConnectError) as exc:
            c.start()

        assert isinstance(exc.value.exc, axonapi.http.requests.exceptions.ConnectTimeout)

    def test_connect_error(self):
        """Pass."""
        c = connect.Connect(
            url="https://127.0.0.1:3919", key=BAD_CRED, secret=BAD_CRED, certwarn=False
        )

        c._http._CONNECT_TIMEOUT = 1

        with pytest.raises(exceptions.ConnectError) as exc:
            c.start()
        assert isinstance(
            exc.value.exc, axonapi.http.requests.exceptions.ConnectionError
        )

    def test_invalid_creds_nowrap(self, request):
        """Pass."""
        ax_url = utils.get_url(request)

        c = connect.Connect(
            url=ax_url, key=BAD_CRED, secret=BAD_CRED, certwarn=False, wraperror=False
        )

        c._http._CONNECT_TIMEOUT = 1

        with pytest.raises(exceptions.InvalidCredentials):
            c.start()

    def test_other_exc(self, request):
        """Pass."""
        c = connect.Connect(
            url="127.0.0.1", key=BAD_CRED, secret=BAD_CRED, certwarn=False
        )

        c._http._CONNECT_TIMEOUT = 1
        c._auth._creds = None

        with pytest.raises(exceptions.ConnectError):
            c.start()

    def test_reason(self):
        """Pass."""
        exc = Exception("badwolf")

        reason = connect.Connect._get_exc_reason(exc)

        assert format(reason) == "badwolf"
