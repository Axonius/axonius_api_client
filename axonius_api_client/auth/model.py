# -*- coding: utf-8 -*-
"""Authentication models."""
import abc
import logging
import typing as t

from ..api.api_endpoint import ApiEndpoint
from ..api.api_endpoints import ApiEndpoints
from ..api.json_api.account import CurrentUser
from ..constants.logs import LOG_LEVEL_AUTH
from ..exceptions import NotLoggedIn
from ..http import Http
from ..logs import get_obj_log


class AuthModel(abc.ABC):
    """Abstract base class for all Authentication methods."""

    is_logged_in: bool = False
    """If login has been called successfully or not."""

    http: t.ClassVar[Http] = None
    """HTTP client to use to send requests."""

    LOG: t.ClassVar[logging.Logger] = None
    """Logger for this object."""

    LOGIN_RESPONSE: t.ClassVar[t.Any] = None
    """Response from login request."""

    VALIDATE_RESPONSE: t.ClassVar[t.Any] = None
    """Response from validate request."""

    CLIENT: t.ClassVar[t.Any] = None
    """Client object to use for API calls."""

    def __init__(self, http: Http, creds: t.Any, log_level: t.Union[int, str] = LOG_LEVEL_AUTH):
        """Mixins for Auth Models.

        Args:
            http: HTTP client to use to send requests.
            creds: Credentials used by this Auth method.
            log_level: Logging level to use for this object.
        """
        self.LOG: t.ClassVar[logging.Logger] = get_obj_log(obj=self, level=log_level)
        self.http: t.ClassVar[Http] = http
        self._creds: t.Any = creds

    @abc.abstractmethod
    def login(self) -> bool:
        """Login to API."""
        raise NotImplementedError()

    def validate(self) -> bool:
        """Validate credentials."""
        self.VALIDATE_RESPONSE: t.ClassVar[t.Any] = ApiEndpoints.account.validate.perform_request(
            http=self.http
        )
        self.LOG.debug(f"Successfully logged in using {self.fields}")
        return True

    @abc.abstractmethod
    def logout(self) -> bool:
        """Logout from API."""
        raise NotImplementedError()

    def get_api_keys(self) -> dict:
        """Get the API key and secret for the current user."""
        return self._get_api_keys()

    def get_current_user(self) -> CurrentUser:
        """Get the current user."""
        return self._get_current_user()

    def check_login(self):
        """Check if login has been called.

        Raises:
            :exc:`NotLoggedIn`:
                When login has not been called before trying to make a call with this Auth model.

        """
        if not self.is_logged_in:
            raise NotLoggedIn(f"Must call login() on {self}")

    @property
    def fields(self) -> t.List[str]:
        """Credential fields used by this auth model."""
        return []

    @property
    def url(self) -> str:
        """Get the URL used by this Auth model."""
        return self.http.url

    def __str__(self) -> str:
        """Show object info."""
        items: t.List[str] = [
            f"url={self.url!r}",
            f"is_logged_in={self.is_logged_in}",
        ]
        items: str = ", ".join(items)
        return f"{self.__class__.__name__}({items})"

    def __repr__(self) -> str:
        """Show object info."""
        return self.__str__()

    def _get_current_user(self) -> CurrentUser:
        """Direct API method to get the current user."""
        endpoint: ApiEndpoint = ApiEndpoints.account.get_current_user
        response: CurrentUser = endpoint.perform_request(http=self.http)
        return response

    def _get_api_keys(self, http_args: t.Optional[dict] = None) -> dict:
        """Direct API method to get the API keys for the current user."""
        endpoint: ApiEndpoint = ApiEndpoints.account.get_api_keys
        response: dict = endpoint.perform_request(http=self.http, http_args=http_args)
        return response
