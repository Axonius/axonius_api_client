# -*- coding: utf-8 -*-
"""Easy all-in-one connection handler."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re

import requests

from . import api, auth, constants, exceptions, http, logs, tools

# TODO examples


class Connect(object):
    """Easy all-in-one connection handler."""

    REASON_RES = [
        re.compile(r".*?object at.*?\>\: ([a-zA-Z0-9\]\[: ]+)"),
        re.compile(r".*?\] (.*) "),
    ]
    """:obj:`list` of patterns`: patterns to look for in exceptions that we can
    pretty up for user display."""

    def __init__(
        self,
        url,
        key,
        secret,
        wraperror=True,
        certpath=None,
        certverify=False,
        certwarn=True,
        cert_client_key=None,
        cert_client_cert=None,
        cert_client_both=None,
        proxy=None,
        save_history=False,
        log_request_attrs=False,
        log_response_attrs=False,
        log_request_body=False,
        log_response_body=False,
        log_logger=logs.LOG,
        log_level_package=constants.LOG_LEVEL_PACKAGE,
        log_level_http=constants.LOG_LEVEL_HTTP,
        log_level_auth=constants.LOG_LEVEL_AUTH,
        log_level_api=constants.LOG_LEVEL_API,
        log_level_console=constants.LOG_LEVEL_CONSOLE,
        log_level_file=constants.LOG_LEVEL_FILE,
        log_console=False,
        log_file=False,
        log_file_name=constants.LOG_FILE_NAME,
        log_file_path=constants.LOG_FILE_PATH,
        log_file_max_mb=constants.LOG_FILE_MAX_MB,
        log_file_max_files=constants.LOG_FILE_MAX_FILES,
    ):
        """Easy all-in-one connection handler.

        Args:
            url (:obj:`str`): URL, hostname, or IP address of Axonius instance
            key (:obj:`str`): API Key from account page in Axonius instance
            secret (:obj:`str`): API Secret from account page in Axonius instance
            wraperror (:obj:`bool`, optional): default ``True``

                * if ``True`` wrap exceptions so that they are more user friendly
                * if ``False`` print the original exception with the full traceback
            certpath (:obj:`str`, optional): default ``None`` -
                path to CA bundle file to use when verifing certs offered by :attr:`url`
                instead of the system CA bundle
            certverify (:obj:`bool`, optional): default ``False`` - control
                validation of certs offered by :attr:`url`:

                * if ``True`` raise exception if cert is invalid/self-signed
                * if ``False`` only raise exception if cert is invalid
            certwarn (:obj:`bool`, optional): default ``True`` - show warnings from
                requests about certs offered by :attr:`url` that are self signed:

                * if ``True`` show warning only the first time it happens
                * if ``False`` never show warning
                * if ``None`` show warning every time it happens
            cert_client_key (:obj:`str`, optional):
                default ``None`` - path to private key file for cert_client_cert to
                offer to :attr:`url` (*must also supply cert_client_cert*)
            cert_client_cert (:obj:`str`, optional):
                default ``None`` - path to cert file to offer to :attr:`url`
                (*must also supply cert_client_key*)
            cert_client_both (:obj:`str`, optional):
                default ``None`` - path to cert file containing both the private key and
                cert to offer to :attr:`url`
            proxy (:obj:`str`, optional): default ``None`` - proxy to use
                when making https requests to :attr:`url`
            save_history (:obj:`bool`, optional): default ``True`` -

                * if ``True`` append responses to
                  :attr:`axonius_api_client.http.Http.HISTORY`
                * if ``False`` do not append responses to
                  :attr:`axonius_api_client.http.Http.HISTORY`
            log_request_attrs (:obj:`bool`): default ``None`` - control logging
              of request attributes:

              * if ``True``, log request attributes defined in
                :data:`axonius_api_client.constants.LOG_REQUEST_ATTRS_VERBOSE`
              * if ``False``, log request attributes defined in
                :data:`axonius_api_client.constants.LOG_REQUEST_ATTRS_BRIEF`
              * if ``None``, do not log any request attributes
            log_response_attrs (:obj:`bool`): default ``None`` - control logging
              of response attributes:

              * if ``True``, log response attributes defined in
                :data:`axonius_api_client.constants.LOG_RESPONSE_ATTRS_VERBOSE`
              * if ``False``, log response attributes defined in
                :data:`axonius_api_client.constants.LOG_RESPONSE_ATTRS_BRIEF`
              * if ``None``, do not log any response attributes
            log_request_body (:obj:`bool`): default ``False`` - control logging
              of request bodies:

              * if ``True``, log request bodies
              * if ``False``, do not log request bodies
            log_response_body (:obj:`bool`): default ``False`` - control logging
              of response bodies:

              * if ``True``, log response bodies
              * if ``False``, do not log response bodies

            log_logger (:obj:`logging.Logger`, optional):
                default :data:`axonius_api_client.logs.LOG`
                logger to use as package root logger
            log_level_package (:obj:`str`, optional):
                default :data:`axonius_api_client.constants.LOG_LEVEL_PACKAGE`
                log level to use for log_logger
            log_level_http (:obj:`str`, optional):
                default :data:`axonius_api_client.constants.LOG_LEVEL_HTTP`
                log level to use for :obj:`axonius_api_client.http.Http`
            log_level_auth (:obj:`str`, optional):
                default :data:`axonius_api_client.constants.LOG_LEVEL_AUTH`
                log level to use for all subclasses of
                :obj:`axonius_api_client.auth.Mixins`
            log_level_api (:obj:`str`, optional):
                default :data:`axonius_api_client.constants.LOG_LEVEL_API`
                log level to use for all subclasses of
                :obj:`axonius_api_client.api.mixins.Mixins`
            log_level_console (:obj:`str`, optional):
                default :data:`axonius_api_client.constants.LOG_LEVEL_CONSOLE`
                log level to use for logs sent to console
            log_level_file (:obj:`str`, optional):
                default :data:`axonius_api_client.constants.LOG_LEVEL_FILE`
                log level to use for logs sent to file
            log_console (:obj:`bool`, optional): default ``False`` -

                * if ``True``, enable logging to console
                * if ``False``, do not log to console
            log_file (:obj:`bool`, optional): default ``False`` -

                * if ``True``, enable logging to file
                * if ``False``, do not log to console
            log_file_name (:obj:`str`, optional):
                default :data:`axonius_api_client.constants.LOG_FILE_NAME`
                name of file to write logs to under log_file_path
            log_file_path (:obj:`str`, optional):
                default :data:`axonius_api_client.constants.LOG_FILE_PATH`
                path to write log_file_name to
            log_file_max_mb (:obj:`str`, optional):
                default :data:`axonius_api_client.constants.LOG_FILE_MAX_MB`
                rollover file logs at this many MB
            log_file_max_files (:obj:`str`, optional):
                default :data:`axonius_api_client.constants.LOG_FILE_MAX_FILES`
                number of rollover file logs to keep
        """
        self._started = False
        self._start_dt = None
        self._wraperror = wraperror
        self.url = url
        """:obj:`str`: URL to connect to"""

        logs.set_level(obj=log_logger, level=log_level_package)

        self._handler_file = None
        self._handler_con = None

        if log_console:
            self._handler_con = logs.add_stderr(obj=log_logger, level=log_level_console)

        if log_file:
            self._handler_file = logs.add_file(
                obj=log_logger,
                level=log_level_file,
                file_path=log_file_path,
                file_name=log_file_name,
                max_mb=log_file_max_mb,
                max_files=log_file_max_files,
            )

        self._http_args = {
            "url": url,
            "https_proxy": proxy,
            "certpath": certpath,
            "certwarn": certwarn,
            "certverify": certverify,
            "cert_client_both": cert_client_both,
            "cert_client_cert": cert_client_cert,
            "cert_client_key": cert_client_key,
            "log_level": log_level_http,
            "log_request_attrs": log_request_attrs,
            "log_response_attrs": log_response_attrs,
            "log_request_body": log_request_body,
            "log_response_body": log_response_body,
            "save_history": save_history,
        }

        self._auth_args = {"key": key, "secret": secret, "log_level": log_level_auth}

        self._http = http.Http(**self._http_args)

        self._auth = auth.ApiKey(http=self._http, **self._auth_args)

        self._api_args = {"auth": self._auth, "log_level": log_level_api}

    def start(self):
        """Connect to and authenticate with Axonius."""
        if not self._started:
            try:
                self._auth.login()
            except Exception as exc:
                if not self._wraperror:
                    raise

                msg_pre = "Unable to connect to {url!r}".format(url=self._http.url)

                if isinstance(exc, requests.exceptions.ConnectTimeout):
                    msg = "{pre}: connection timed out after {t} seconds"
                    msg = msg.format(pre=msg_pre, t=self._http.CONNECT_TIMEOUT)
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

            self._started = True
            self._start_dt = tools.dt_now()

    @property
    def users(self):
        """Get the object for user assets API.

        Returns:
            :obj:`axonius_api_client.api.assets.Users`
        """
        self.start()
        if not hasattr(self, "_users"):
            self._users = api.Users(**self._api_args)
        return self._users

    @property
    def devices(self):
        """Get the object for user assets API.

        Returns:
            :obj:`axonius_api_client.api.assets.Devices`
        """
        self.start()
        if not hasattr(self, "_devices"):
            self._devices = api.Devices(**self._api_args)
        return self._devices

    @property
    def adapters(self):
        """Get the object for adapters API.

        Returns:
            :obj:`axonius_api_client.api.adapters.Adapters`
        """
        self.start()
        if not hasattr(self, "_adapters"):
            self._adapters = api.Adapters(**self._api_args)
        return self._adapters

    @property
    def enforcements(self):
        """Get the object for enforcements API.

        Returns:
            :obj:`axonius_api_client.api.enforcements.Enforcements`
        """
        self.start()
        if not hasattr(self, "_enforcements"):
            self._enforcements = api.Enforcements(**self._api_args)
        return self._enforcements

    @property
    def system(self):
        """Get the object for system API.

        Returns:
            :obj:`axonius_api_client.api.system.System`
        """
        self.start()
        if not hasattr(self, "_system"):
            self._system = api.System(**self._api_args)
        return self._system

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        client = getattr(self, "_http", "")
        url = getattr(client, "url", self._http_args["url"])
        if self._started:
            uptime = tools.dt_sec_ago(self._start_dt)
            return "Connected to {url!r} for {uptime}".format(uptime=uptime, url=url)
        else:
            return "Not connected to {url!r}".format(url=url)

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    @classmethod
    def _get_exc_reason(cls, exc):
        """Trim exceptions down to a more user friendly display.

        Uses :attr:`REASON_RES` to do regex substituions.

        Args:
            exc (:obj:`Exception`): Exception to trim down.

        Returns:
            :obj:`str`: prettied up str if match found, else original exception str
        """
        reason = format(exc)
        for reason_re in cls.REASON_RES:
            if reason_re.search(reason):
                return reason_re.sub(r"\1", reason).rstrip("')")
        return reason
