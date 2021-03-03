# -*- coding: utf-8 -*-
"""Authentication via API key and API secret."""
from typing import List

from ..exceptions import AlreadyLoggedIn
from ..http import Http
from .models import Mixins


class ApiKey(Mixins):
    """Authentication method using API key & API secret."""

    def __init__(self, http: Http, key: str, secret: str, **kwargs):
        """Authenticate using API key & API secret.

        Args:
            http: HTTP client to use to send requests
            key: API key to use in credentials
            secret: API secret to use in credentials

        """
        if isinstance(key, str):
            key = key.strip()

        if isinstance(secret, str):
            secret = secret.strip()

        creds = {"key": key, "secret": secret}
        super().__init__(http=http, creds=creds, **kwargs)

    def login(self):
        """Login to API."""
        if self.is_logged_in:
            raise AlreadyLoggedIn(f"Already logged in on {self}")

        self.http.session.headers["api-key"] = self._creds["key"]
        self.http.session.headers["api-secret"] = self._creds["secret"]
        self._validate()
        self._logged_in = True
        self.LOG.debug(f"Successfully logged in using {self._cred_fields}")

    def logout(self):
        """Logout from API."""
        super().logout()

    @property
    def _cred_fields(self) -> List[str]:
        """Credential fields used by this auth model."""
        return ["key", "secret"]

    def _logout(self):
        """Logout from API."""
        self._logged_in = False
        self.http.session.headers = {}
