# -*- coding: utf-8 -*-
"""Authentication via API key and API secret."""
import typing as t

from ..http import Http
from ..tools import strip_str
from .model import AuthModel


class AuthApiKey(AuthModel):
    """Authentication method using API key & API secret."""

    def __init__(self, http: Http, key: str, secret: str, **kwargs):
        """Authenticate using API key & API secret.

        Args:
            http: HTTP client to use to send requests
            key: API key to use in credentials
            secret: API secret to use in credentials

        """
        creds: t.Dict[str, str] = {"key": strip_str(key), "secret": strip_str(secret)}
        kwargs["creds"] = creds
        super().__init__(http=http, **kwargs)

    def login(self) -> bool:
        """Login to API."""
        if not self.is_logged_in:
            self.http.session.headers["api-key"] = self._creds["key"]
            self.http.session.headers["api-secret"] = self._creds["secret"]
            self.is_logged_in = self.validate()
            return True
        return False

    @property
    def fields(self) -> t.List[str]:
        """Credential fields used by this auth model."""
        return ["key", "secret"]

    def logout(self) -> bool:
        """Logout from API."""
        if self.is_logged_in:
            self.http.session.headers.pop("api-key", None)
            self.http.session.headers.pop("api-secret", None)
            self.is_logged_in = False
            return True
        return False
