# -*- coding: utf-8 -*-
"""Null authentication method."""
from ..http import Http
from .model import AuthModel


class AuthNull(AuthModel):
    """Null authentication method."""

    def __init__(self, http: Http, **kwargs):
        """Authenticate using no credentials.

        Args:
            http: HTTP client to use to send requests
        """
        kwargs["creds"] = None
        super().__init__(http=http, **kwargs)

    def login(self) -> bool:
        """Login to API."""
        if not self.is_logged_in:
            self.is_logged_in = True
            return True
        return False

    def logout(self) -> bool:
        """Logout from API."""
        if self.is_logged_in:
            self.is_logged_in = False
            return True
        return False
