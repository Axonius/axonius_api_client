# -*- coding: utf-8 -*-
"""Exceptions and warnings."""


class AxonWarning(Warning):
    """Warnings for :mod:`axonius_api_client`."""


class ApiWarning(AxonWarning):
    """Warnings for :mod:`.api`."""


class AxonError(Exception):
    """Errors for :mod:`axonius_api_client`."""


class ApiError(AxonError):
    """Errors for :mod:`.api`."""


class ToolsError(AxonError):
    """Errors for :mod:`.tools`."""


class AuthError(AxonError):
    """Errors for :mod:`.auth`."""


class NotFoundError(ApiError):
    """Error when something is not found."""


class InvalidCredentials(AuthError):
    """Error when credentials are invalid."""


class NotLoggedIn(AuthError):
    """Error when not logged in."""


class AlreadyLoggedIn(AuthError):
    """Error when already logged in."""


class ConnectError(AxonError):
    """Error in :obj:`.connect.Connect`."""


class HttpError(AxonError):
    """Errors for :mod:`.http`."""


class ConfigError(ApiError):
    """Pass."""


class ConfigInvalidValue(ConfigError):
    """Pass."""


class ConfigUnchanged(ConfigError):
    """Pass."""


class ConfigUnknown(ConfigError):
    """Pass."""


class ConfigRequired(ConfigError):
    """Pass."""


class CnxError(ApiError):
    """Errors for :obj:`.api.adapters.Cnx`."""


class CnxGoneError(CnxError):
    """Errors for :obj:`.api.adapters.Cnx`."""


class CnxUpdateError(CnxError):
    """Pass."""


class CnxTestError(CnxError):
    """Pass."""


class CnxAddError(CnxError):
    """Pass."""


class ResponseError(ApiError):
    """Errors when checking responses."""


class ResponseNotOk(ResponseError):
    """Error if response has a status code that is an error and error_status is True."""


class JsonInvalid(ResponseError):
    """Error when response has invalid JSON."""


class JsonError(ResponseError):
    """Error when JSON has key:error that is not empty or key:status=error."""


class WizardError(ApiError):
    pass


class SectionParserKeyError(ApiError):
    def __init__(self, parser, key, msg):
        self.parser = parser
        self.key = key
        self.msg = msg

        err = f"Error in section {parser.name!r} with {key.key!r} key: {msg}"
        section_lines = [f"  {k}: {v!r}" for k, v in parser.unparsed.items()]

        lines = [
            err,
            "",
            f"Supplied Section: {parser.name}",
            *section_lines,
            "",
            "Key documentation:",
            parser.wizard.doc_section_key(key=key),
            "",
            err,
        ]
        super().__init__("\n".join(lines))
