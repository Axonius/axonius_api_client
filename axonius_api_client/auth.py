# -*- coding: utf-8 -*-
"""Authentication methods."""
import abc
import logging
from typing import List

from .api.routers import API_VERSION
from .constants import LOG_LEVEL_AUTH
from .exceptions import AlreadyLoggedIn, AuthError, InvalidCredentials, NotLoggedIn
from .http import Http
from .logs import get_obj_log
from .tools import json_reload


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
        """Throw exc if not login."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractproperty
    def http(self) -> Http:
        """Get HttpClient object."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractproperty
    def is_logged_in(self) -> bool:
        """Check if login has been called."""
        raise NotImplementedError  # pragma: no cover


class Mixins:
    """Mixins for Model."""

    _logged_in: bool = False
    """:obj:`bool`: Attribute checked by :meth:`is_logged_in`."""

    def __init__(self, http: Http, creds: dict, **kwargs):
        """Mixins for Model.

        Args:
            http (:obj:`.http.Http`):
                HTTP client to use to send requests.
            creds:
                Credentials used by this Auth method.

        """
        log_level = kwargs.get("log_level", LOG_LEVEL_AUTH)
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        """:obj:`logging.Logger`: Logger for this object."""

        self._http: Http = http
        """:obj:`.http.Http`: HTTP Client."""

        self._creds: dict = creds
        """:obj:`dict`: Credential store."""

        self._check_http_lock()
        self._set_http_lock()

    def __str__(self) -> str:
        """Show object info.

        Returns:
            :obj:`str`

        """
        bits = [f"url={self.http.url!r}", f"is_logged_in={self.is_logged_in}"]
        bits = ", ".join(bits)
        return f"{self.__class__.__module__}.{self.__class__.__name__}({bits})"

    def __repr__(self) -> str:
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    @property
    def http(self) -> Http:
        """Get HttpClient object.

        Returns:
            :obj:`.http.Http`

        """
        return self._http

    def _check_http_lock(self):
        """Check HTTP client not already used by another Auth.

        Raises:
            :exc:`AuthError`

        """
        auth_lock = getattr(self.http, "_auth_lock", None)
        if auth_lock:
            raise AuthError(f"{self.http} already being used by {auth_lock}")

    def _set_http_lock(self):
        """Set HTTP Client auth lock."""
        self._http._auth_lock = self

    def _validate(self):
        """Validate credentials."""
        # XXX fallback to old auth path, remove once everyone is 3.5+
        paths = [API_VERSION.system.meta_about, API_VERSION.devices.count]
        for path in paths:
            response = self.http(method="get", path=path)
            body = json_reload(obj=response.text, error=False)
            self.LOG.debug(f"Received auth path {path!r} body:\n{body}")
            if response.ok:
                break

        try:
            response.raise_for_status()
        except Exception as exc:
            self._logged_in = False
            raise InvalidCredentials(
                f"Invalid credentials on {self} -- exception: {exc}"
            )

        self._logged_in = True

    def logout(self):
        """Logout from API."""
        self.check_login()
        self._logged_in = False
        self._logout()

    def check_login(self):
        """Throw exc if not login.

        Raises:
            :exc:`NotLoggedIn`

        """
        if not self.is_logged_in:
            raise NotLoggedIn(f"Must call login() on {self}")

    @property
    def is_logged_in(self) -> bool:
        """Check if login has been called.

        Returns:
            :obj:`bool`

        """
        return self._logged_in


class ApiKey(Mixins, Model):
    """Authentication method using API key & API secret."""

    def __init__(self, http: Http, key: str, secret: str, **kwargs):
        """Authenticate using API key & API secret.

        Args:
            http (:obj:`.http.Http`):
                HTTP client to use to send requests.
            key (:obj:`str`):
                API key to use in credentials.
            secret (:obj:`str`):
                API secret to use in credentials.

        """
        creds = {"key": key, "secret": secret}
        super(ApiKey, self).__init__(http=http, creds=creds, **kwargs)

    @property
    def _cred_fields(self) -> List[str]:
        return ["key", "secret"]

    def _logout(self):
        """Logout from API."""
        self._logged_in = False
        self.http.session.headers = {}

    def login(self):
        """Login to API."""
        if self.is_logged_in:
            raise AlreadyLoggedIn(f"Already logged in on {self}")

        self.http.session.headers["api-key"] = self._creds["key"]
        self.http.session.headers["api-secret"] = self._creds["secret"]
        self._validate()
        self._logged_in = True
        self.LOG.debug(f"Successfully logged in using {self._cred_fields}")
