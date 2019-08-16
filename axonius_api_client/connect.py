# -*- coding: utf-8 -*-
"""Axon Connection class."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import re

import requests

from . import api, auth, exceptions, http, constants, logs


class Connect(object):
    """Pass."""

    _REASON_RES = [
        re.compile(r".*?object at.*?\>\: ([a-zA-Z0-9\]\[: ]+)"),
        re.compile(r".*?\] (.*) "),
    ]

    @classmethod
    def _get_exc_reason(cls, exc):
        """Pass."""
        reason = format(exc)
        for reason_re in cls._REASON_RES:
            if reason_re.search(reason):
                return reason_re.sub(r"\1", reason).rstrip("')")
        return reason

    def __init__(self, url, key, secret, **kwargs):
        """Pass."""
        self._started = False
        self._start_dt = None
        self._wraperror = kwargs.get("wraperror", True)

        proxy = kwargs.get("proxy", "")
        certpath = kwargs.get("certpath", "")
        certverify = kwargs.get("certverify", False)
        certwarn = kwargs.get("certwarn", True)
        log_logger = kwargs.get("log_logger", logs.LOG)
        log_level_package = kwargs.get("log_level_package", constants.LOG_LEVEL_PACKAGE)
        log_level_http = kwargs.get("log_level_http", constants.LOG_LEVEL_HTTP)
        log_level_auth = kwargs.get("log_level_auth", constants.LOG_LEVEL_AUTH)
        log_level_api = kwargs.get("log_level_api", constants.LOG_LEVEL_API)
        log_level_console = kwargs.get("log_level_console", constants.LOG_LEVEL_CONSOLE)
        log_level_file = kwargs.get("log_level_file", constants.LOG_LEVEL_FILE)
        log_console = kwargs.get("log_console", False)
        log_console_method = kwargs.get("log_console_method", logs.add_stderr)
        log_file = kwargs.get("log_file", False)
        log_file_method = kwargs.get("log_file_method", logs.add_file)
        log_file_name = kwargs.get("log_file_name", constants.LOG_FILE_NAME)
        log_file_path = kwargs.get("log_file_path", constants.LOG_FILE_PATH)
        log_file_max_mb = kwargs.get("log_file_max_mb", constants.LOG_FILE_MAX_MB)
        log_file_max_files = kwargs.get(
            "log_file_max_files", constants.LOG_FILE_MAX_FILES
        )

        logs.set_level(obj=log_logger, level=log_level_package)

        if log_console:
            self._handler_con = log_console_method(
                obj=log_logger, level=log_level_console
            )
        else:
            self._handler_con = None

        if log_file:
            self._handler_file = log_file_method(
                obj=log_logger,
                level=log_level_file,
                file_path=log_file_path,
                file_name=log_file_name,
                max_mb=log_file_max_mb,
                max_files=log_file_max_files,
            )
        else:
            self._handler_file = None

        self._http_args = {
            "url": url,
            "https_proxy": proxy,
            "certpath": certpath,
            "certwarn": certwarn,
            "certverify": certverify,
            "log_level": log_level_http,
        }
        self._auth_args = {"key": key, "secret": secret, "log_level": log_level_auth}

        self._http = http.HttpClient(**self._http_args)
        self._auth = auth.AuthKey(http_client=self._http, **self._auth_args)

        self._api_args = {"auth": self._auth, "log_level": log_level_api}

    def start(self):
        """Pass."""
        if self._started:
            return

        try:
            self._auth.login()
        except Exception as exc:
            if not self._wraperror:
                raise

            msg_pre = "Unable to connect to {url!r}".format(url=self._http.url)

            if isinstance(exc, requests.exceptions.ConnectTimeout):
                msg = "{pre}: connection timed out after {t} seconds"
                msg = msg.format(pre=msg_pre, t=self._http.connect_timeout)
                raise exceptions.ConnectError(msg=msg, exc=exc)
            elif isinstance(exc, requests.exceptions.ConnectionError):
                msg = "{pre}: {reason}"
                msg = msg.format(pre=msg_pre, reason=self._get_exc_reason(exc=exc))
                raise exceptions.ConnectError(msg=msg, exc=exc)
            elif isinstance(exc, exceptions.InvalidCredentials):
                msg = "{pre}: Invalid Credentials supplied"
                msg = msg.format(pre=msg_pre, url=self._http.url)
                raise exceptions.ConnectError(msg=msg, exc=exc)

            msg = "{pre}: {exc}"
            msg = msg.format(pre=msg_pre, exc=exc)
            raise exceptions.ConnectError(msg=msg, exc=exc)

        self.users = api.Users(**self._api_args)
        self.devices = api.Devices(**self._api_args)
        self.enforcements = api.Enforcements(**self._api_args)
        self.actions = api.Actions(**self._api_args)
        self.adapters = api.Adapters(**self._api_args)

        self._started = True
        self._start_dt = datetime.datetime.utcnow()

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        client = getattr(self, "_http", "")
        url = getattr(client, "url", self._http_args["url"])
        if self._started:
            uptime = datetime.datetime.utcnow() - self._start_dt
            uptime = format(uptime).split(".")[0]
            return "Connected to {url!r} for {uptime}".format(uptime=uptime, url=url)
        else:
            return "Not connected to {url!r}".format(url=url)

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()
