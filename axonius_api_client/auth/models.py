# -*- coding: utf-8 -*-
"""Authentication models."""
import abc
import logging

from ..api.routers import API_VERSION
from ..constants.logs import LOG_LEVEL_AUTH
from ..exceptions import AuthError, InvalidCredentials, NotLoggedIn
from ..http import Http
from ..logs import get_obj_log
from ..tools import json_reload
from ..version import __version__


class Model:
    """Abstract base class for all Authentication methods."""

    @abc.abstractmethod
    def login(self):
        """Login to API."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def logout(self):
        """Logout from API."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def check_login(self):
        """Throw exc if not logged in."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractproperty
    def http(self) -> Http:
        """Get Http object."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractproperty
    def is_logged_in(self) -> bool:
        """Check if login has been called."""
        raise NotImplementedError  # pragma: no cover


class Mixins(Model):
    """Mixins for Auth Models."""

    _logged_in: bool = False
    """Attribute checked by :meth:`is_logged_in`."""

    _validate_path: str = API_VERSION.system.meta_about
    """Endpoint to use to validate logins."""

    def __init__(self, http: Http, creds: dict, **kwargs):
        """Mixins for Auth Models.

        Args:
            http: HTTP client to use to send requests.
            creds: Credentials used by this Auth method.

        """
        log_level = kwargs.get("log_level", LOG_LEVEL_AUTH)
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        """Logger for this object."""

        self._http: Http = http
        """HTTP Client."""

        self._creds: dict = creds
        """Credential store."""

        self._check_http_lock()
        self._set_http_lock()

    @property
    def http(self) -> Http:
        """Get HttpClient object."""
        return self._http

    def logout(self):
        """Logout from API."""
        self.check_login()
        self._logged_in = False
        self._logout()

    def check_login(self):
        """Check if login has been called.

        Raises:
            :exc:`NotLoggedIn`:
                When login has not been called before trying to make a call with this Auth model.

        """
        if not self.is_logged_in:
            raise NotLoggedIn(f"Must call login() on {self}")

    @property
    def is_logged_in(self) -> bool:
        """Check if login has been called."""
        return self._logged_in

    def __str__(self) -> str:
        """Show object info."""
        bits = [f"url={self.http.url!r}", f"is_logged_in={self.is_logged_in}"]
        bits = ", ".join(bits)
        return f"{self.__class__.__module__}.{self.__class__.__name__}({bits})"

    def __repr__(self) -> str:
        """Show object info."""
        return self.__str__()

    def _check_http_lock(self):
        """Check HTTP client not already used by another Auth.

        Raises:
            :exc:`AuthError`:
                When the HTTP client supplied is already being used by another Auth method.

        """
        auth_lock = getattr(self.http, "_auth_lock", None)
        if auth_lock:
            raise AuthError(f"{self.http} already being used by {auth_lock}")

    def _set_http_lock(self):
        """Set HTTP Client auth lock."""
        self._http._auth_lock = self

    def _validate(self):
        """Validate credentials."""
        response = self.http(method="get", path=self._validate_path)
        if response.status_code == 404:
            raise AuthError(
                f"Unable to access endpoint {self._validate_path}, "
                f"API client v{__version__} requires Axonius v3.9 or above"
            )

        body = json_reload(obj=response.text, error=False)
        self.LOG.debug(f"Received auth path {self._validate_path!r} body:\n{body}")

        try:
            response.raise_for_status()
        except Exception as exc:
            self._logged_in = False
            raise InvalidCredentials(f"Invalid credentials on {self} -- exception: {exc}")

        self._logged_in = True
