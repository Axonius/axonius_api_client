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


class AuthUser(models.ApiVersion1, models.AuthMixins, models.AuthBase):
    """Authentication method using username & password."""

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

        self._check_http_lock()
        self._set_http_lock()

    def _logout(self):
        """Logout from API."""
        self.http_client.session.auth = None

    def login(self):
        """Login to API."""
        if self.is_logged_in:
            raise exceptions.AlreadyLoggedIn(auth=self)

        self.http_client.session.auth = (
            self._creds["username"],
            self._creds["password"],
        )

        try:
            self.validate()
        except Exception:
            self._logout()
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


class AuthKey(models.ApiVersion1, models.AuthMixins, models.AuthBase):
    """Authentication method using API key & API secret."""

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

        self._check_http_lock()
        self._set_http_lock()

    def _logout(self):
        """Logout from API."""
        self.http_client.session.headers.pop("api-key", None)
        self.http_client.session.headers.pop("api-secret", None)

    def login(self):
        """Login to API."""
        if self.is_logged_in:
            raise exceptions.AlreadyLoggedIn(auth=self)

        self.http_client.session.headers.update(self._creds)

        try:
            self.validate()
        except Exception:
            self._logout()
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
