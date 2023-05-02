# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import axonius_api_client as axonapi
import logging

import pytest

from axonius_api_client.connect import Connect
from axonius_api_client.exceptions import ConnectError, InvalidCredentials
from axonius_api_client.http import requests
from axonius_api_client.api import json_api

from ..utils import IS_LINUX, get_url, get_connect

BAD_CRED = "tardis"


class TestConnect:
    def test_log_http_max(self, request):
        client = get_connect(request, log_http_max=True)
        assert client.LOG_HTTP_MAX is True
        assert client.ARGS_HTTP["log_request_body"] is True
        assert client.ARGS_HTTP["log_response_body"] is True
        assert client.ARGS_HTTP["log_request_attrs"] == "all"
        assert client.ARGS_HTTP["log_response_attrs"] == "all"
        assert client.ARGS_HTTP["log_body_lines"] >= 10000

    def test_check_binding(self, test_no_start, request):
        ax_url = get_url(request)

        with pytest.raises(ConnectError):
            Connect(url=ax_url, key=BAD_CRED, secret=BAD_CRED, http=test_no_start.http)

    def test_set_log_level_connect(self, test_start):
        test_start.set_log_level_connect("info")
        assert test_start.LOG.level == logging.INFO

    def test_set_log_level_http(self, test_start):
        test_start.set_log_level_http("warning")
        assert test_start.http.LOG.level == logging.WARNING

    def test_set_log_level_auth(self, test_start):
        test_start.set_log_level_auth("error")
        assert test_start.auth.LOG.level == logging.ERROR

    def test_set_log_level_package(self, test_start):
        test_start.set_log_level_package("debug")
        assert axonapi.LOG.level == logging.DEBUG

    def test_set_log_level_api(self, test_start):
        str(test_start.settings_gui)
        test_start.set_log_level_api("error")
        assert test_start.API_LOG_LEVEL == "ERROR"
        assert test_start.settings_ip.LOG.level == logging.ERROR
        assert test_start.settings_gui.LOG.level == logging.ERROR

    def test_control_log_console(self, request):
        client = get_connect(request)

        result = client.control_log_console(True)
        assert result is True
        assert client.HANDLER_CON

        client.set_log_level_console("critical")
        assert client.HANDLER_CON.level == logging.CRITICAL

        result = client.control_log_console(True)
        assert result is False
        assert client.HANDLER_CON

        result = client.control_log_console(False)
        assert result is True
        assert client.HANDLER_CON is None

        result = client.control_log_console(False)
        assert result is False
        assert client.HANDLER_CON is None

    def test_control_log_file(self, request, tmp_path):
        log_file_name = tmp_path / "test.log"
        client = get_connect(request, log_file_name=log_file_name)

        result = client.control_log_file(True)
        assert result is True
        assert client.HANDLER_FILE

        client.set_log_level_file("info")
        assert client.HANDLER_FILE.level == logging.INFO

        result = client.control_log_file(True, rotate=True)
        assert result is False
        assert client.HANDLER_FILE

        result = client.control_log_file(False)
        assert result is True
        assert client.HANDLER_FILE is None

        result = client.control_log_file(False)
        assert result is False
        assert client.HANDLER_FILE is None

    def test_ssl_days_left(self, test_no_start):
        assert test_no_start.ssl_days_left > 0

    def test_get_api_keys(self, test_start):
        assert isinstance(test_start.api_keys, dict) and test_start.api_keys

    @pytest.fixture(scope="class")
    def test_no_start(self, request):
        client = get_connect(request, key=BAD_CRED, secret=BAD_CRED, timeout_connect=1)
        assert "Not connected" in format(client)
        assert "Not connected" in repr(client)
        assert client.HANDLER_FILE is None
        assert client.HANDLER_CON is None
        yield client

    def test_jdump(self, test_no_start):
        test_no_start.jdump(test_no_start)

    def test_no_start_logs(self, request):
        client = get_connect(request, log_console=True, log_file=True)
        assert "Not connected" in format(client)
        assert "Not connected" in repr(client)
        assert isinstance(client.HANDLER_FILE, logging.Handler)
        assert isinstance(client.HANDLER_CON, logging.Handler)

    @pytest.fixture(scope="class")
    def test_start(self, request):
        client = get_connect(request)
        client.start()
        assert "Connected" in format(client)
        assert "Connected" in repr(client)
        for attr in client.API_ATTRS:
            value = getattr(client, attr)
            assert format(value)
            assert repr(value)
        yield client

    def test_current_user(self, test_start):
        user = test_start.current_user
        assert isinstance(user, json_api.account.CurrentUser)

    def test_invalid_creds(self, request):
        client = get_connect(request, key=BAD_CRED, secret=BAD_CRED, timeout_connect=1)
        with pytest.raises(ConnectError) as exc:
            client.start()
        assert isinstance(exc.value.exc, InvalidCredentials)

    def test_connect_timeout(self):
        client = Connect(
            url="127.0.0.99",
            key=BAD_CRED,
            secret=BAD_CRED,
            certwarn=False,
            timeout_connect=1,
        )
        with pytest.raises(ConnectError) as exc:
            client.start()

        exp_exc = requests.ConnectionError if IS_LINUX else requests.ConnectTimeout
        assert isinstance(exc.value.exc, exp_exc)

    def test_connect_error(self):
        client = Connect(
            url="https://127.0.0.1:3919",
            key=BAD_CRED,
            secret=BAD_CRED,
            certwarn=False,
            timeout_connect=1,
        )
        with pytest.raises(ConnectError) as exc:
            client.start()
        assert isinstance(exc.value.exc, requests.ConnectionError)

    def test_invalid_creds_nowrap(self, request):
        client = get_connect(
            request, key=BAD_CRED, secret=BAD_CRED, timeout_connect=1, wraperror=False
        )
        with pytest.raises(InvalidCredentials):
            client.start()

    def test_other_exc(self):
        client = Connect(
            url="127.0.0.1",
            certwarn=False,
            key=BAD_CRED,
            secret=BAD_CRED,
            timeout_connect=1,
        )
        with pytest.raises(ConnectError):
            client.start()

    def test_reason(self):
        exc = Exception("badwolf")
        reason = Connect._get_exc_reason(exc)
        assert format(reason) == "badwolf"
