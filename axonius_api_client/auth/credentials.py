# -*- coding: utf-8 -*-
"""Authentication via API key and API secret."""
import typing as t

from ..api.api_endpoints import ApiEndpoint
from ..api.json_api.account import LoginRequest, LoginResponse
from ..http import Http
from .models import Mixins


class Credentials(Mixins):
    """Authentication method using username and password credentials."""

    def __init__(
        self,
        http: Http,
        username: t.Optional[str] = None,
        password: t.Optional[str] = None,
        **kwargs,
    ):
        """Authenticate using username and password.

        Args:
            http (Http): HTTP client to use to send requests
            username (t.Optional[str], optional): Axonius User Name
            password (t.Optional[str], optional): Axonius Password
            prompt (bool, optional): Prompt for credentials that are not non-empty strings
        """
        creds: LoginRequest = LoginRequest(user_name=username, password=password, eula_agreed=True)
        super().__init__(http=http, creds=creds, **kwargs)

    def login(self):
        """Login to API."""
        if not self.is_logged_in:
            self._creds.check_credentials()
            self._login_response: LoginResponse = self._login(request_obj=self._creds)
            headers: dict = {"authorization": self._login_response.authorization}
            self._api_keys: dict = self._get_api_keys(headers=headers)
            self.http.session.headers["api-key"] = self._api_keys["api_key"]
            self.http.session.headers["api-secret"] = self._api_keys["api_secret"]
            self._validate()
            self._logged_in = True
            self.LOG.debug(f"Successfully logged in using {self._cred_fields}")

    def logout(self):
        """Logout from API."""
        super().logout()

    def _login(self, request_obj: LoginRequest) -> LoginResponse:
        """Direct API method to issue a login request.

        Args:
            request_obj (LoginRequest): Request object to send

        Returns:
            LoginResponse: Response object received
        """
        endpoint: ApiEndpoint = self.endpoints.login
        response: LoginResponse = endpoint.perform_request(http=self.http, request_obj=request_obj)
        return response

    @property
    def _cred_fields(self) -> t.List[str]:
        """Credential fields used by this auth model."""
        return [f"username={self._creds.user_name!r}", "password"]

    def _logout(self):
        """Logout from API."""
        self._logged_in = False
        self.http.session.headers = {}
