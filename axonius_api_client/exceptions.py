# -*- coding: utf-8 -*-
"""Exceptions and warnings."""
from typing import List, Optional, Union

import requests


def get_exc_str(exc: Optional[Exception] = None) -> str:
    """Pass."""
    if exc:
        return f"Original exception {type(exc)}: {exc}"
    return ""


class AxonWarning(Warning):
    """Base class for all warnings in this package."""


class ApiWarning(AxonWarning):
    """Warnings for API models."""


class GuiQueryWizardWarning(ApiWarning):
    """Pass."""


class UnknownFieldSchema(ApiWarning):
    """Warning for unknown field schema mappings."""


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


class SavedQueryNotFoundError(NotFoundError):
    """Error when something is not found."""

    def __init__(self, details: str, sqs: List[Union[dict, object]]):
        """Pass."""
        from .parsers.tables import tablize_sqs

        self.sqs = sqs
        self.details = details
        self.msg = f"Saved Query not found with {details}"
        self.tablemsg = tablize_sqs(data=sqs, err=self.msg)
        super().__init__(self.tablemsg)


class SavedQueryTagsNotFoundError(SavedQueryNotFoundError):
    """Error when something is not found."""

    def __init__(self, value: List[str], valid: List[str]):
        """Pass."""
        self.value = value
        self.valid = valid

        value_txt = ", ".join(value)
        valid_txt = "\n" + "\n".join(valid)
        self.msg = f"Saved Query not found with tags: {value_txt}, valid tags:{valid_txt}"
        super(NotFoundError, self).__init__(self.msg)


class AlreadyExists(ApiError):
    """Error when something exists with same name."""


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
        from .tools import json_log

        url = response.url
        method = response.request.method
        code = response.status_code
        reason = response.reason
        out_len = len(response.request.body or "")
        in_len = len(response.text or "")

        msg = msg or "Error in REST API response"
        pre = [
            msg,
            get_exc_str(exc=exc),
            f"URL: {url!r}, METHOD: {method}",
            f"CODE: {code!r}, REASON: {reason!r}, BYTES OUT: {out_len}, BYTES IN: {in_len}",
        ]
        middle = [
            "Request Object:",
            json_log(obj=response.request.body),
            "Response Object:",
            json_log(obj=response.text),
        ]
        msgs = [*pre, "", *middle, "", *pre]
        return "\n".join(msgs)


class InvalidCredentials(ResponseError):
    """Error when credentials are invalid."""


class ResponseNotOk(ResponseError):
    """Error if response has a status code that is an error and error_status is True."""


class JsonInvalidError(ResponseError):
    """Error when response has invalid JSON."""


class JsonError(ResponseError):
    """Error when JSON has key:error that is not empty or key:status=error."""


class WizardError(ApiError):
    """Errors in query wizards."""


class ApiAttributeExtraWarning(ApiWarning):
    """Pass."""


class ApiAttributeError(ApiError):
    """Pass."""


class ApiAttributeTypeError(ApiAttributeError):
    """Pass."""


class ApiAttributeMissingError(ApiAttributeError):
    """Pass."""


class NoTriggerDefinedError(ApiError):
    """Pass."""


class StopFetch(ApiError):
    """Pass."""

    def __init__(self, reason: str, state: dict):
        """Pass."""
        self.reason = reason
        self.state = state
        super().__init__(reason)


class SchemaError(ApiError):
    """Pass."""

    def __init__(self, obj, schema, exc, data):
        """Pass."""
        from .tools import json_log, prettify_obj

        self.schema = schema
        self.exc = exc
        self.obj = obj
        self.data = data

        errors = []
        if hasattr(exc, "messages"):
            errors = exc.messages
            if isinstance(errors, dict) and "errors" in errors:
                errors = errors["errors"]
            errors = prettify_obj(errors)

        pre = f"Schema Validation Error in {schema}"
        self.errors = [
            pre,
            f"From object: {obj}",
            get_exc_str(exc=exc),
            "",
            "While trying to load data:",
            f"{json_log(data)}",
            *errors,
            "",
            pre,
        ]
        self.msg = "\n".join(self.errors)
        super().__init__(self.msg)


class RequestError(ApiError):
    """Pass."""

    def __init__(
        self,
        api_endpoint,
        err: str,
        details: Optional[List[str]] = None,
        exc: Optional[Exception] = None,
    ):
        """Pass."""
        self.api_endpoint = api_endpoint
        self.err = err
        self.details = details or []
        self.exc = exc
        self.errors = [
            err,
            get_exc_str(exc=exc),
            f"While in {api_endpoint}",
            "",
            *details,
            "",
            err,
        ]
        self.msg = "\n".join(self.errors)
        super().__init__(self.msg)


class RequestMissingArgsError(RequestError):
    """Pass."""


class RequestObjectTypeError(RequestError):
    """Pass."""


class RequestFormatError(RequestError):
    """Pass."""


class RequestFormatPathError(RequestFormatError):
    """Pass."""


class RequestFormatObjectError(RequestFormatError):
    """Pass."""


class RequestLoadObjectError(RequestError):
    """Pass."""


class ResponseLoadObjectError(RequestError):
    """Pass."""


class FeatureNotEnabledError(ApiError):
    """Pass."""

    def __init__(self, name: str):
        """Pass."""
        msg = (
            f"The {name} feature is not enabled on this instance, "
            "please contact support@axonius.com to enable"
        )
        super().__init__(msg)
