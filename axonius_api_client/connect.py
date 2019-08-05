# -*- coding: utf-8 -*-
"""Axon Connection class."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
import re

import requests

from . import api, auth, exceptions, http

LOG = logging.getLogger(__name__)


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

    def __init__(
        self,
        url,
        key,
        secret,
        proxy="",
        certpath="",
        certverify=False,
        certwarn=True,
        wraperror=True,
        **kwargs
    ):
        """Pass."""
        self._log = LOG.getChild(self.__class__.__name__)
        self._started = False
        self._start_dt = None
        self._client_args = {
            "url": url,
            "https_proxy": proxy,
            "certpath": certpath,
            "certwarn": certwarn,
            "certverify": certverify,
        }
        self._auth_args = {"key": key, "secret": secret}
        self._wraperror = wraperror
        self._kwargs = kwargs
        self._client = http.HttpClient(**self._client_args)

    def start(self):
        """Pass."""
        if self._started:
            return

        try:
            self._auth = auth.AuthKey(http_client=self._client, **self._auth_args)
            self._auth.login()
        except Exception as exc:
            if not self._wraperror:
                raise

            msg_pre = "Unable to connect to {url!r}".format(url=self._client.url)

            if isinstance(exc, requests.exceptions.ConnectTimeout):
                msg = "{pre}: connection timed out after {t} seconds"
                msg = msg.format(pre=msg_pre, t=self._client.connect_timeout)
                raise exceptions.ConnectError(msg=msg, exc=exc)
            elif isinstance(exc, requests.exceptions.ConnectionError):
                msg = "{pre}: {reason}"
                msg = msg.format(pre=msg_pre, reason=self._get_exc_reason(exc=exc))
                raise exceptions.ConnectError(msg=msg, exc=exc)
            elif isinstance(exc, exceptions.InvalidCredentials):
                msg = "{pre}: Invalid Credentials supplied for {url!r}"
                msg = msg.format(pre=msg_pre, url=self._client.url)
                raise exceptions.ConnectError(msg=msg, exc=exc)

            msg = "{pre}: {exc}"
            msg = msg.format(pre=msg_pre, exc=exc)
            raise exceptions.ConnectError(msg=msg, exc=exc)

        self.users = api.Users(auth=self._auth)
        self.devices = api.Devices(auth=self._auth)
        self.enforcements = api.Enforcements(auth=self._auth)
        self.actions = api.Actions(auth=self._auth)
        self.adapters = api.Adapters(auth=self._auth)
        self._started = True
        self._start_dt = datetime.datetime.utcnow()

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        client = getattr(self, "_client", "")
        url = getattr(client, "url", self._client_args["url"])
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
