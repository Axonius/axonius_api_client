# -*- coding: utf-8 -*-
"""Exceptions and warnings."""


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


class InvalidCredentials(AuthError):
    """Error when credentials are invalid."""


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


class ResponseNotOk(ResponseError):
    """Error if response has a status code that is an error and error_status is True."""


class JsonInvalid(ResponseError):
    """Error when response has invalid JSON."""


class JsonError(ResponseError):
    """Error when JSON has key:error that is not empty or key:status=error."""


class WizardError(ApiError):
    """Errors in query wizards."""
