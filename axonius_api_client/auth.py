# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from . import models
from . import exceptions

LOG = logging.getLogger(__name__)


class AuthUser(models.AuthBase):
    """Authentication method using username & password."""

    _API_VERSION = 1
    """:obj:`int`: Version of the API this ApiClient is made for."""

    _API_PATH = "api/V{version}/".format(version=_API_VERSION)
    """:obj:`str`: Base path of API."""

    def __init__(self, http_client, username, password):
        """Constructor.

        Args:
            http_client (:obj:`axonius_api_client.http.HttpClient`):
                HTTP client to use to send requests.
            username (:obj:`str`):
                Username to use in credentials.
            password (:obj:`str`):
                Password to use in credentials.

        """
        self._log = LOG.getChild(self.__class__.__name__)
        """:obj:`logging.Logger`: Logger for this object."""

        self._http_client = http_client
        """:obj:`axonius_api_client.http.HttpClient`: HTTP Client."""

        self._creds = {"username": username, "password": password}
        """:obj:`dict`: Credential store."""

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
            :obj:`axonius_api_client.http.HttpClient`

        """
        return self._http_client

    def _validate(self):
        """Validate credentials.

        Raises:
            :exc:`exceptions.InvalidCredentials`

        """
        response = self._http_client(
            method="get", path=self._API_PATH, route="devices/count"
        )

        if response.status_code in [401, 403]:
            msg = "Login failed!"
            raise exceptions.InvalidCredentials(msg)

        response.raise_for_status()

    def logout(self):
        """Logout from API."""
        self.http_client.session.cookies.clear()
        self.http_client.session.headers.pop("api-key", None)
        self.http_client.session.headers.pop("api-secret", None)
        self.http_client.session.auth = None

    def login(self):
        """Login to API."""
        self.logout()

        self.http_client.session.auth = (
            self._creds["username"],
            self._creds["password"],
        )

        try:
            self._validate()
        except Exception:
            self.logout()
            raise

        msg = "Successfully logged in with username & password"
        self._log.debug(msg)

    @property
    def is_logged_in(self):
        """Check if login has been called.

        Returns:
            :obj:`bool`

        """
        return bool(self.http_client.session.auth)


class AuthKey(models.AuthBase):
    """Authentication method using API key & API secret."""

    _API_VERSION = 1
    """:obj:`int`: Version of the API this ApiClient is made for."""

    _API_PATH = "api/V{version}/".format(version=_API_VERSION)
    """:obj:`str`: Base path of API."""

    def __init__(self, http_client, key, secret):
        """Constructor.

        Args:
            http_client (:obj:`axonius_api_client.http.HttpClient`):
                HTTP client to use to send requests.
            key (:obj:`str`):
                API key to use in credentials.
            secret (:obj:`str`):
                API secret to use in credentials.

        """
        self._log = LOG.getChild(self.__class__.__name__)
        """:obj:`logging.Logger`: Logger for this object."""

        self._http_client = http_client
        """:obj:`axonius_api_client.http.HttpClient`: HTTP Client."""

        self._creds = {"api-key": key, "api-secret": secret}
        """:obj:`dict`: Credential store."""

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
            :obj:`axonius_api_client.http.HttpClient`

        """
        return self._http_client

    def _validate(self):
        """Validate credentials.

        Raises:
            :exc:`exceptions.InvalidCredentials`

        """
        response = self.http_client(
            method="get", path=self._API_PATH, route="devices/count"
        )

        if response.status_code in [401, 403]:
            msg = "Login failed!"
            raise exceptions.InvalidCredentials(msg)

        response.raise_for_status()

    def logout(self):
        """Logout from API."""
        self.http_client.session.cookies.clear()
        self.http_client.session.headers.pop("api-key", None)
        self.http_client.session.headers.pop("api-secret", None)
        self.http_client.session.auth = None

    def login(self):
        """Login to API."""
        self.logout()

        self.http_client.session.headers.update(self._creds)

        try:
            self._validate()
        except Exception:
            self.logout()
            raise

        msg = "Successfully logged in with API key & secret"
        self._log.debug(msg)

    @property
    def is_logged_in(self):
        """Check if login has been called.

        Returns:
            :obj:`bool`

        """
        key = "api-key" in self.http_client.session.headers
        secret = "api-secret" in self.http_client.session.headers
        return all([key, secret])
