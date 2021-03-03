# -*- coding: utf-8 -*-
"""Exceptions and warnings."""
from typing import Optional

import requests


class AxonWarning(Warning):
    """Base class for all warnings in this package."""


class ApiWarning(AxonWarning):
    """Warnings for API models."""


class AxonError(Exception):
    """Base class for all exceptions in this package."""


class ApiError(AxonError):
    """Errors for API models."""


class ToolsError(AxonError):
    """Errors for tools."""


class AuthError(AxonError):
    """Errors for authentication models."""


class NotFoundError(ApiError):
    """Error when something is not found."""


class NotLoggedIn(AuthError):
    """Error when not logged in."""


class AlreadyLoggedIn(AuthError):
    """Error when already logged in."""


class ConnectError(AxonError):
    """Error in connect client."""


class HttpError(AxonError):
    """Errors for HTTP client."""


class ConfigError(ApiError):
    """Errors in a configuration."""


class ConfigInvalidValue(ConfigError):
    """Error when a supplied configuration has a bad type or is the wrong choice."""


class ConfigUnchanged(ConfigError):
    """Error when a supplied configuration is no different from the current configuration."""


class ConfigUnknown(ConfigError):
    """Error when an unknown configuration key is supplied."""


class ConfigRequired(ConfigError):
    """Error when a required configuration key is not supplied."""


class CnxError(ApiError):
    """Errors for connections."""


class CnxGoneError(CnxError):
    """Errors when a connection has gone away."""


class CnxUpdateError(CnxError):
    """Errors when updating a connections configuration."""


class CnxTestError(CnxError):
    """Errors when testing a connections configuration."""


class CnxAddError(CnxError):
    """Errors when adding a new connection."""


class ResponseError(ApiError):
    """Errors when checking responses."""

    def __init__(self, msg: Optional[str] = None, response=None, exc: Optional[Exception] = None):
        """Error in responses received from REST API.

        Args:
            response (:obj:`requests.Response`): response that originated the error
            msg: error message to include in exception
            exc: original exception that was thrown if any
        """
        self.response: requests.Response = response
        self.exc: Exception = exc
        self.msg: str = msg
        self.errmsg: str = self.build_errmsg(response=response, msg=msg, exc=exc)
        super().__init__(self.errmsg)

    @classmethod
    def build_errmsg(
        cls, response, msg: Optional[str] = None, exc: Optional[Exception] = None
    ) -> str:
        """Build an error message from a response.

        Args:
            response (:obj:`requests.Response`): response that originated the error
            msg: error message to include in exception
            exc: exception that was thrown if any
        """
        from .constants.logs import MAX_BODY_LEN
        from .tools import json_dump, json_load, prettify_obj

        msgs = []

        url = response.url
        method = response.request.method
        code = response.status_code
        reason = response.reason
        out_len = len(response.request.body or "")
        in_len = len(response.text or "")

        msgs += [
            *([f"Original exception: {exc}"] if exc else []),
            "",
            f"URL: {url!r}, METHOD: {method}",
            f"CODE: {code!r}, REASON: {reason!r}, BYTES OUT: {out_len}, BYTES IN: {in_len}",
            "",
        ]
        request_obj = json_load(obj=response.request.body, error=False)
        response_obj = json_load(obj=response.text, error=False)

        if isinstance(request_obj, (dict, list, tuple)):
            msgs += ["Request Object:", json_dump(obj=request_obj, error=False)]
        else:
            msgs += ["Request Body:", str(request_obj)[:MAX_BODY_LEN]]

        if isinstance(response_obj, (dict, list, tuple)):
            msgs += ["Response Object:", *prettify_obj(response_obj)]
        else:
            msgs += ["Response Body:", str(response_obj)[:MAX_BODY_LEN]]

        msg = msg or "Error in REST API response"
        msgs = [msg, *msgs, "", msg]

        return "\n".join(msgs)


class InvalidCredentials(ResponseError):
    """Error when credentials are invalid."""


class ResponseNotOk(ResponseError):
    """Error if response has a status code that is an error and error_status is True."""


class JsonInvalid(ResponseError):
    """Error when response has invalid JSON."""


class JsonError(ResponseError):
    """Error when JSON has key:error that is not empty or key:status=error."""


class WizardError(ApiError):
    """Errors in query wizards."""


class StopFetch(ApiError):
    """Pass."""

    def __init__(self, reason: str, state: dict):
        """Pass."""
        self.reason = reason
        self.state = state
        super().__init__(reason)
