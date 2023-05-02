# -*- coding: utf-8 -*-
"""Authentication via username and password."""
import typing as t

from ..http import Http
from .model import AuthModel
from ..api.json_api.account import LoginRequest, LoginResponse
from ..api.api_endpoints import ApiEndpoint, ApiEndpoints


class AuthCredentials(AuthModel):
    """Authentication method using username and password credentials."""

    def __init__(
        self,
        http: Http,
        username: str,
        password: str,
        **kwargs,
    ):
        """Authenticate using username and password.

        Args:
            http: HTTP client to use to send requests
            username: Axonius Username
            password: Axonius Password
        """
        creds: LoginRequest = LoginRequest(user_name=username, password=password, eula_agreed=True)
        kwargs["creds"] = creds
        super().__init__(http=http, **kwargs)

    def login(self):
        """Login to API."""
        if not self.is_logged_in:
            self.LOGIN_RESPONSE: t.ClassVar[LoginResponse] = self._login(request_obj=self._creds)
            # now that we logged in with username & password
            # get the API keys and use for the rest of the session
            api_keys: dict = self._get_api_keys(http_args=self.LOGIN_RESPONSE.http_args)
            self.http.session.headers["api-key"] = api_keys["api_key"]
            self.http.session.headers["api-secret"] = api_keys["api_secret"]
            self.is_logged_in = self.validate()
            return True
        return False

    def logout(self):
        """Logout from API."""
        if self.is_logged_in:
            self.http.session.headers.pop("api-key", None)
            self.http.session.headers.pop("api-secret", None)
            self.is_logged_in = False
            return True
        return False

    @property
    def fields(self) -> t.List[str]:
        """Credential fields used by this auth model."""
        return [f"username={self._creds.user_name!r}", "password"]

    def _login(self, request_obj: LoginRequest) -> LoginResponse:
        """Direct API method to issue a login request using credentials.

        Args:
            request_obj (LoginRequest): Request object to send

        Returns:
            LoginResponse: Response object received
        """
        endpoint: ApiEndpoint = ApiEndpoints.account.login
        response: LoginResponse = endpoint.perform_request(http=self.http, request_obj=request_obj)
        return response
