# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .. import exceptions, models
from . import mixins


class AuthUser(mixins.AuthMixins, models.AuthModel):
    """Authentication method using username & password."""

    def __init__(self, http_client, username, password, **kwargs):
        """Constructor.

        Args:
            http_client (:obj:`axonius_api_client.http.interfaces.HttpClient`):
                HTTP client to use to send requests.
            username (:obj:`str`):
                Username to use in credentials.
            password (:obj:`str`):
                Password to use in credentials.

        """
        creds = {"username": username, "password": password}
        super(AuthUser, self).__init__(http_client=http_client, creds=creds, **kwargs)

    @property
    def _cred_fields(self):
        return ["username", "password"]

    def _logout(self):
        """Logout from API."""
        self._logged_in = False
        self.http_client.session.auth = None

    def login(self):
        """Login to API."""
        if self.is_logged_in:
            raise exceptions.AlreadyLoggedIn(auth=self)

        self.http_client.session.auth = (
            self._creds["username"],
            self._creds["password"],
        )

        self._validate()

        self._logged_in = True
        msg = "Successfully logged in using {}".format(self._cred_fields)
        self._log.debug(msg)
