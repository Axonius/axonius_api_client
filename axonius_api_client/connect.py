# -*- coding: utf-8 -*-
"""Easy all-in-one connection handler."""
import logging
import pathlib
import re
from typing import List, Optional, Union

import requests

from .api.adapters import Adapters
from .api.assets import Devices, Users
from .api.enforcements import Enforcements
from .api.enforcements.actions import RunAction
from .api.system import System
from .auth import ApiKey
from .constants import (
    LOG_FILE_MAX_FILES,
    LOG_FILE_MAX_MB,
    LOG_FILE_NAME,
    LOG_FILE_PATH,
    LOG_LEVEL_API,
    LOG_LEVEL_AUTH,
    LOG_LEVEL_CONSOLE,
    LOG_LEVEL_FILE,
    LOG_LEVEL_HTTP,
    LOG_LEVEL_PACKAGE,
    TIMEOUT_CONNECT,
    TIMEOUT_RESPONSE,
)
from .exceptions import ConnectError, InvalidCredentials
from .http import Http
from .logs import LOG, add_file, add_stderr, get_obj_log, set_log_level
from .tools import json_dump, sysinfo
from .version import __version__ as VERSION


class Connect:
    """Easy all-in-one connection handler."""

    REASON_RES: List[str] = [
        re.compile(r".*?object at.*?\>\: ([a-zA-Z0-9\]\[: ]+)"),
        re.compile(r".*?\] (.*) "),
    ]
    """:obj:`list` of patterns`: patterns to look for in exceptions that we can
    pretty up for user display."""

    def __init__(
        self,
        url: str,
        key: str,
        secret: str,
        wraperror: bool = True,
        timeout_connect: int = TIMEOUT_CONNECT,
        timeout_response: int = TIMEOUT_RESPONSE,
        certpath: Optional[Union[str, pathlib.Path]] = None,
        certverify: bool = False,
        certwarn: bool = True,
        cert_client_key: Optional[Union[str, pathlib.Path]] = None,
        cert_client_cert: Optional[Union[str, pathlib.Path]] = None,
        cert_client_both: Optional[Union[str, pathlib.Path]] = None,
        proxy: Optional[str] = None,
        save_history: bool = False,
        log_level: Union[str, int] = "debug",
        log_request_attrs: Optional[List[str]] = None,
        log_response_attrs: Optional[List[str]] = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
        log_logger: logging.Logger = LOG,
        log_level_package: Union[str, int] = LOG_LEVEL_PACKAGE,
        log_level_http: Union[str, int] = LOG_LEVEL_HTTP,
        log_level_auth: Union[str, int] = LOG_LEVEL_AUTH,
        log_level_api: Union[str, int] = LOG_LEVEL_API,
        log_level_console: Union[str, int] = LOG_LEVEL_CONSOLE,
        log_level_file: Union[str, int] = LOG_LEVEL_FILE,
        log_console: bool = False,
        log_file: bool = False,
        log_file_name: Union[str, pathlib.Path] = LOG_FILE_NAME,
        log_file_path: Union[str, pathlib.Path] = LOG_FILE_PATH,
        log_file_max_mb: int = LOG_FILE_MAX_MB,
        log_file_max_files: int = LOG_FILE_MAX_FILES,
    ):
        """Easy all-in-one connection handler.

        Args:
            url (:obj:`str`): URL, hostname, or IP address of Axonius instance
            key (:obj:`str`): API Key from account page in Axonius instance
            secret (:obj:`str`): API Secret from account page in Axonius instance
            timeout_connect (:obj:`int`, optional):
                default :data:`TIMEOUT_CONNECT` - seconds to
                wait for connections to open to :attr:`url`
            timeout_response (:obj:`int`, optional):
                default :data:`TIMEOUT_RESPONSE` - seconds to
                wait for responses from :attr:`url`
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
                :data:`axonius_api_client.LOG_REQUEST_ATTRS_VERBOSE`
              * if ``False``, log request attributes defined in
                :data:`axonius_api_client.LOG_REQUEST_ATTRS_BRIEF`
              * if ``None``, do not log any request attributes
            log_response_attrs (:obj:`bool`): default ``None`` - control logging
              of response attributes:

              * if ``True``, log response attributes defined in
                :data:`axonius_api_client.LOG_RESPONSE_ATTRS_VERBOSE`
              * if ``False``, log response attributes defined in
                :data:`axonius_api_client.LOG_RESPONSE_ATTRS_BRIEF`
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
                default :data:`axonius_api_client.LOG`
                logger to use as package root logger
            log_level_package (:obj:`str`, optional):
                default :data:`axonius_api_client.LOG_LEVEL_PACKAGE`
                log level to use for log_logger
            log_level_http (:obj:`str`, optional):
                default :data:`axonius_api_client.LOG_LEVEL_HTTP`
                log level to use for :obj:`axonius_api_client.http.Http`
            log_level_auth (:obj:`str`, optional):
                default :data:`axonius_api_client.LOG_LEVEL_AUTH`
                log level to use for all subclasses of
                :obj:`axonius_api_client.auth.Mixins`
            log_level_api (:obj:`str`, optional):
                default :data:`axonius_api_client.LOG_LEVEL_API`
                log level to use for all subclasses of
                :obj:`axonius_api_client.mixins.Mixins`
            log_level_console (:obj:`str`, optional):
                default :data:`axonius_api_client.LOG_LEVEL_CONSOLE`
                log level to use for logs sent to console
            log_level_file (:obj:`str`, optional):
                default :data:`axonius_api_client.LOG_LEVEL_FILE`
                log level to use for logs sent to file
            log_console (:obj:`bool`, optional): default ``False`` -

                * if ``True``, enable logging to console
                * if ``False``, do not log to console
            log_file (:obj:`bool`, optional): default ``False`` -

                * if ``True``, enable logging to file
                * if ``False``, do not log to console
            log_file_name (:obj:`str`, optional):
                default :data:`axonius_api_client.LOG_FILE_NAME`
                name of file to write logs to under log_file_path
            log_file_path (:obj:`str`, optional):
                default :data:`axonius_api_client.LOG_FILE_PATH`
                path to write log_file_name to
            log_file_max_mb (:obj:`str`, optional):
                default :data:`axonius_api_client.LOG_FILE_MAX_MB`
                rollover file logs at this many MB
            log_file_max_files (:obj:`str`, optional):
                default :data:`axonius_api_client.LOG_FILE_MAX_FILES`
                number of rollover file logs to keep
        """
        self.LOG = get_obj_log(obj=self, level=log_level)
        self._started = False
        self._wraperror = wraperror
        self.url = url
        """:obj:`str`: URL to connect to"""

        set_log_level(obj=log_logger, level=log_level_package)

        self._handler_file = None
        self._handler_con = None

        if log_console:
            self._handler_con = add_stderr(obj=log_logger, level=log_level_console)

        if log_file:
            self._handler_file = add_file(
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
            "connect_timeout": timeout_connect,
            "response_timeout": timeout_response,
        }

        self._auth_args = {"key": key, "secret": secret, "log_level": log_level_auth}

        self._http = Http(**self._http_args)

        self._auth = ApiKey(http=self._http, **self._auth_args)

        self._api_args = {"auth": self._auth, "log_level": log_level_api}

    def start(self):
        """Connect to and authenticate with Axonius."""
        if not self._started:
            sysinfo_dump = json_dump(sysinfo())
            LOG.debug(f"SYSTEM INFO: {sysinfo_dump}")

            try:
                self._auth.login()
            except Exception as exc:
                if not self._wraperror:
                    raise

                pre = f"Unable to connect to {self._http.url!r}"

                if isinstance(exc, requests.ConnectTimeout):
                    timeout = self._http.CONNECT_TIMEOUT
                    msg = f"{pre}: connection timed out after {timeout} seconds"
                    cnxexc = ConnectError(msg)
                elif isinstance(exc, requests.ConnectionError):
                    reason = self._get_exc_reason(exc=exc)
                    cnxexc = ConnectError(f"{pre}: {reason}")
                elif isinstance(exc, InvalidCredentials):
                    cnxexc = ConnectError(f"{pre}: Invalid Credentials supplied")
                else:
                    cnxexc = ConnectError(f"{pre}: {exc}")
                cnxexc.exc = exc
                raise cnxexc

            self._started = True
            LOG.info(str(self))

    @property
    def users(self) -> Users:
        """Get the object for user assets API.

        Returns:
            :obj:`axonius_api_client.api.assets.Users`
        """
        self.start()
        if not hasattr(self, "_users"):
            self._users = Users(**self._api_args)
        return self._users

    @property
    def devices(self) -> Devices:
        """Get the object for user assets API.

        Returns:
            :obj:`axonius_api_client.assets.Devices`
        """
        self.start()
        if not hasattr(self, "_devices"):
            self._devices = Devices(**self._api_args)
        return self._devices

    @property
    def adapters(self) -> Adapters:
        """Get the object for adapters API.

        Returns:
            :obj:`axonius_api_client.adapters.Adapters`
        """
        self.start()
        if not hasattr(self, "_adapters"):
            self._adapters = Adapters(**self._api_args)
        return self._adapters

    @property
    def enforcements(self) -> Enforcements:
        """Get the object for enforcements API.

        Returns:
            :obj:`axonius_api_client.enforcements.Enforcements`
        """
        self.start()
        if not hasattr(self, "_enforcements"):
            self._enforcements = Enforcements(**self._api_args)
        return self._enforcements

    @property
    def run_actions(self) -> RunAction:
        """Get the object for run actions API.

        Returns:
            :obj:`axonius_api_client.actions.RunAction`
        """
        self.start()
        if not hasattr(self, "_run_actions"):
            self._run_actions = RunAction(**self._api_args)
        return self._run_actions

    @property
    def system(self) -> System:
        """Get the object for system API.

        Returns:
            :obj:`axonius_api_client.system.System`
        """
        self.start()
        if not hasattr(self, "_system"):
            self._system = System(**self._api_args)
        return self._system

    def __str__(self) -> str:
        """Show object info.

        Returns:
            :obj:`str`

        """
        client = getattr(self, "_http", "")
        url = getattr(client, "url", self._http_args["url"])
        if self._started:
            about = self.system.meta.about()
            version = about.get("Version", "") or "DEMO"
            version = version.replace("_", ".")
            built = about.get("Build Date", "")
            return (
                f"Connected to {url!r} version {version} (RELEASE DATE: {built})"
                f" with API Client v{VERSION}"
            )
        else:
            return f"Not connected to {url!r}"

    def __repr__(self) -> str:
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    @classmethod
    def _get_exc_reason(cls, exc: Exception) -> str:
        """Trim exceptions down to a more user friendly display.

        Uses :attr:`REASON_RES` to do regex substituions.

        Args:
            exc (:obj:`Exception`): Exception to trim down.

        Returns:
            :obj:`str`: prettied up str if match found, else original exception str
        """
        reason = str(exc)
        for reason_re in cls.REASON_RES:
            if reason_re.search(reason):
                return reason_re.sub(r"\1", reason).rstrip("')")
        return reason
