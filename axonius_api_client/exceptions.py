"""Exceptions and warnings."""
import typing as t

import requests


def get_exc_str(exc: t.Optional[Exception] = None) -> str:
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


class ExtraAttributeWarning(ApiWarning):
    """Pass."""


class UnknownFieldSchema(ApiWarning):
    """Warning for unknown field schema mappings."""


class AxonError(Exception):
    """Base class for all exceptions in this package."""

    def __init__(self, msg: t.Union[str, t.List[t.Any]]) -> None:
        """Pass."""
        if isinstance(msg, (list, tuple)):
            msg = "\n".join([str(x) for x in msg])
        super().__init__(msg)


class AxonTypeError(AxonError):
    """Pass."""

    def __init__(
        self,
        attr: str,
        value: t.Any,
        expected: t.Any,
        src: t.Any = None,
        extra: t.Any = None,
    ) -> None:
        """Pass."""
        self.src: t.Any = src
        self.attr: str = attr
        self.value: t.Any = value
        self.expected: t.Any = expected
        self.extra: t.Any = extra
        err: str = f"Incorrect value type supplied to {attr!r}"
        msgs: t.List[str] = [
            err,
            "",
            f"Source: {src}",
            f"Supplied value: {value!r}",
            f"Supplied value type: {type(value)}",
            f"Expected value type: {expected!r}",
            "",
            err,
        ]
        if extra:
            if isinstance(extra, (list, tuple)):
                msgs += [str(x) for x in extra]
            else:
                msgs.append(str(extra))
        super().__init__(msgs)


class ApiError(AxonError):
    """Errors for API models."""


class ConfirmNotTrue(AxonError):
    """Error for when confirm != True."""

    def __init__(
        self,
        confirm: t.Any = False,
        prompt: t.Any = False,
        reason: t.Any = "",
        src: t.Any = None,
        extra: t.Any = None,
    ) -> None:
        """Pass."""
        self.confirm: t.Any = confirm
        self.reason: t.Any = reason
        msgs: t.List[str] = [
            f"Unable to {reason}",
            f"confirm is {confirm} and prompt is {prompt}, confirm must be {True}",
        ]
        if src is not None:
            msgs += ["", "While in object:", f"{src!r}"]

        if extra:
            if isinstance(extra, (list, tuple)):
                msgs += [str(x) for x in extra]
            else:
                msgs.append(str(extra))
        super().__init__(msgs)


class NotAllowedError(AxonError):
    """Error when something not allowed."""


class ToolsError(AxonError):
    """Errors for tools."""


class AuthError(AxonError):
    """Errors for authentication models."""


class NotFoundError(ApiError):
    """Error when something is not found."""


class SavedQueryNotFoundError(NotFoundError):
    """Error when something is not found."""

    def __init__(self, details: str, sqs: t.List[t.Union[dict, object]]) -> None:
        """Pass."""
        from .parsers.tables import tablize_sqs

        self.sqs = sqs
        self.details = details
        self.msg = f"Saved Query not found with {details}"
        try:
            barrier = "#" * 80
            barrier = f"\n{barrier}\n"
            details = barrier + barrier.join([x.str_details for x in sqs])
            self.msg_table = [self.msg, "", details, "", self.msg]
        except Exception:
            self.msg_table = tablize_sqs(data=sqs, err=self.msg)
        super().__init__(self.msg_table)


class SavedQueryTagsNotFoundError(SavedQueryNotFoundError):
    """Error when something is not found."""

    def __init__(self, value: t.List[str], valid: t.List[str]) -> None:
        """Pass."""
        self.value = value
        self.valid = valid

        value_txt = ", ".join(value)
        valid_txt = "\n" + "\n".join(valid)
        self.msg = (
            f"Saved Query not found with tags: {value_txt}, valid tags:{valid_txt}"
        )
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

    cnx_new: t.ClassVar[t.Optional[dict]] = None


class ResponseError(ApiError):
    """Errors when checking responses."""

    def __init__(
        self,
        msg: t.Optional[str] = None,
        response=None,
        exc: t.Optional[Exception] = None,
    ) -> None:
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
        cls,
        response,
        msg: t.Optional[str] = None,
        exc: t.Optional[Exception] = None,
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

    def __init__(self, reason: str, state: dict) -> None:
        """Pass."""
        self.reason = reason
        self.state = state
        super().__init__(reason)


class SchemaError(ApiError):
    """Pass."""

    def __init__(self, obj, schema, exc, data) -> None:
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
        details: t.Optional[t.List[str]] = None,
        exc: t.Optional[Exception] = None,
    ) -> None:
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

    def __init__(self, name: str, extra: t.Optional[str] = None) -> None:
        """Pass."""
        msg = (
            f"The {name} feature is not enabled on this instance, "
            "please contact support@axonius.com to enable"
        )
        if extra is not None:
            msg = f"{msg}:\n{extra}"
        super().__init__(msg)


class RunnerError(ApiError):
    """Pass."""


class RunnerWarning(ApiWarning):
    """Pass."""


class GrabberError(ApiError):
    """Pass."""


class GrabberWarning(ApiWarning):
    """Pass."""


class FolderAlreadyExistsError(AlreadyExists):
    """Error when something exists with same name."""


class FolderNotFoundError(NotFoundError):
    """Error when something is not found."""

    def __init__(self, msg: str, folder: t.Optional[object] = None) -> None:
        """Pass."""
        self.folder: t.Optional[object] = folder
        super().__init__(msg)


class SearchError(AxonError):
    """Pass."""


class SearchUnmatchedError(SearchError):
    """Pass."""


class SearchNoMatchesError(SearchError):
    """Pass."""


class SearchNoObjectsError(SearchError):
    """Pass."""


class DecodeError(ValueError, AxonError):
    """Raised when a byte string cannot be decoded to a valid ObjectId string.

    Attributes:
        value (bytes): The input byte string.
        encoding_format (str): The encoding format used for decoding.
        encoding_errors (str): The error handling method used for decoding.
    """

    def __init__(
        self,
        value: t.Any,
        encoding_format: t.Optional[str] = None,
        encoding_errors: t.Optional[str] = None,
    ) -> None:
        """Initialize a new instance of the DecodeError exception.

        Args:
            value (t.Any):
                The input value.
            encoding_format (t.Optional[str], optional):
                The encoding format used for decoding.
            encoding_errors (t.Optional[str], optional):
                The error handling method used for decoding.
        """
        from .tools import trim_value_repr

        self.value: bytes = value
        self.encoding_format: t.Optional[str] = encoding_format
        self.encoding_errors: t.Optional[str] = encoding_errors
        super().__init__(
            f"The input byte string {trim_value_repr(self.value)} cannot be decoded to a valid "
            f"ObjectId string using encoding_format {self.encoding_format!r} "
            f" and encoding_errors {self.encoding_errors!r}.",
        )


class InvalidObjectIdError(ValueError, AxonError):
    """Raised when an input string is not a valid ObjectId.

    Attributes:
        value (str): The input string.
    """

    def __init__(self, value: str) -> None:
        """Initialize a new instance of the InvalidObjectIdError exception.

        Args:
            value (str): The input string.
        """
        from .tools import trim_value_repr

        self.value: t.Any = value
        super().__init__(
            f"The input string {trim_value_repr(self.value)} is not a valid ObjectId.",
        )


class InvalidTypeError(TypeError, AxonError):
    """Raised when an input value is not one of the allowed types.

    Attributes:
        value (t.Any): The input value.
        allowed_types (t.Tuple[type]): The tuple of allowed types.
    """

    def __init__(
        self,
        value: t.Any,
        allowed_types: t.Optional[t.Tuple[type]] = (),
    ) -> None:
        """Initialize a new instance of the InvalidTypeError exception.

        Args:
            value (t.Any): The input value.
            allowed_types (t.Optional[t.Tuple[type]], optional): The tuple of allowed types.
        """
        self.value: t.Any = value
        self.allowed_types: t.Optional[t.Tuple[type]] = allowed_types
        from .tools import get_type_str

        super().__init__(
            f"The input value {self.value!r} type {get_type_str(self.value)} is not "
            f"one of the allowed types: {get_type_str(allowed_types)}.",
        )


class FormatError(KeyError, AxonError):
    """Raised when there is a KeyError in when doing a string formatting."""

    def __init__(
        self,
        template: str,
        error: Exception,
        args: t.Any = None,
        kwargs: t.Dict[str, t.Any] = None,
    ) -> None:
        """Initialize a new instance of the FormatError exception.

        Args:
            template (str): The string template that had the problem.
            error (Exception): The original error that occurred.
            *args (t.Any): The args passed to the template
            **kwargs (t.Dict[str, t.Any]): The kwargs passed to the template
        """
        self.template: str = template
        self.error: Exception = error
        self.args: t.Any = args
        self.kwargs: t.Dict[str, t.Any] = kwargs

        super().__init__(
            f"Error formatting template {template!r}\n"
            f"{type(self.error)}: {self.error}\n"
            f"args: {self.args}\n",
            f"kwargs: {self.kwargs}\n",
        )
