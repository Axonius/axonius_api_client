# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from .. import api, exceptions, logs

LOG = logging.getLogger(__name__)


class AuthMixins(object):
    """Mixins for AuthModel."""

    _logged_in = False
    """:obj:`bool`: Attribute checked by :meth:`is_logged_in`."""

    def __init__(self, http_client, creds, **kwargs):
        """Constructor.

        Args:
            http_client (:obj:`axonius_api_client.http.interfaces.HttpClient`):
                HTTP client to use to send requests.
            creds:
                Credentials used by this Auth method.

        """
        logger = kwargs.get("logger", logging.getLogger(self.__class__.__module__))
        self._log = logger.getChild(self.__class__.__name__)
        logs.set_level(obj=self._log, level=kwargs.get("log_level", "warning"))

        self._http_client = http_client
        """:obj:`axonius_api_client.http.interfaces.HttpClient`: HTTP Client."""

        self._creds = creds
        """:obj:`dict`: Credential store."""

        self._check_http_lock()
        self._set_http_lock()

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        bits = [
            "url={!r}".format(self.http_client.url),
            "is_logged_in={}".format(self.is_logged_in),
        ]
        bits = "({})".format(", ".join(bits))
        return "{c.__module__}.{c.__name__}{bits}".format(c=self.__class__, bits=bits)

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    @property
    def http_client(self):
        """Get HttpClient object.

        Returns:
            :obj:`axonius_api_client.http.interfaces.HttpClient`

        """
        return self._http_client

    def _check_http_lock(self):
        """Check HTTP client not already used by another Auth.

        Raises:
            :exc:`exceptions.AuthError`

        """
        auth_lock = getattr(self.http_client, "_auth_lock", None)
        if auth_lock:
            msg = "{http_client} already being used by {auth}"
            msg = msg.format(http_client=self.http_client, auth=auth_lock)
            raise exceptions.AuthError(msg)

    def _set_http_lock(self):
        """Set HTTP Client auth lock."""
        self._http_client._auth_lock = self

    def _validate(self):
        """Validate credentials."""
        response = self.http_client(method="get", path=api.routers.ApiV1.devices.count)

        try:
            response.raise_for_status()
        except Exception as exc:
            self._logged_in = False
            raise exceptions.InvalidCredentials(auth=self, exc=exc)

        self._logged_in = True

    def logout(self):
        """Logout from API."""
        self.check_login()
        self._logged_in = False
        self._logout()

    def check_login(self):
        """Throw exc if not login.

        Raises:
            :exc:`exceptions.NotLoggedIn`

        """
        if not self.is_logged_in:
            raise exceptions.NotLoggedIn(auth=self)

    @property
    def is_logged_in(self):
        """Check if login has been called.

        Returns:
            :obj:`bool`

        """
        return self._logged_in
