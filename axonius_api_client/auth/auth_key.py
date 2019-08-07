# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from .. import exceptions, models
from . import mixins

LOG = logging.getLogger(__name__)


class AuthKey(mixins.AuthMixins, models.AuthModel):
    """Authentication method using API key & API secret."""

    def __init__(self, http_client, key, secret):
        """Constructor.

        Args:
            http_client (:obj:`axonius_api_client.http.interfaces.HttpClient`):
                HTTP client to use to send requests.
            key (:obj:`str`):
                API key to use in credentials.
            secret (:obj:`str`):
                API secret to use in credentials.

        """
        super(AuthKey, self).__init__(http_client=http_client, key=key, secret=secret)

    @property
    def _cred_fields(self):
        return ["key", "secret"]

    def _logout(self):
        """Logout from API."""
        self._logged_in = False
        self.http_client.session.headers = {}

    def login(self):
        """Login to API."""
        if self.is_logged_in:
            raise exceptions.AlreadyLoggedIn(auth=self)

        self.http_client.session.headers["api-key"] = self._creds["key"]
        self.http_client.session.headers["api-secret"] = self._creds["secret"]

        self._validate()

        self._logged_in = True

        msg = "Successfully logged in using {}".format(self._cred_fields)
        self._log.debug(msg)
