# -*- coding: utf-8 -*-
"""Parent exception and warnings for this package."""
from __future__ import absolute_import, division, print_function, unicode_literals

from . import tools


class AxonError(Exception):
    """Parent exception for all package errors."""


class AxonWarning(Warning):
    """Pass."""


class ApiError(AxonError):
    """Parent exception for all API errors."""


class ApiWarning(AxonWarning):
    """Parent exception for all API errors."""


class ToolsError(AxonError):
    """Parent exception for all tools errors."""


class AuthError(AxonError):
    """Parent exception for all Authentication errors."""


class HttpError(AxonError):
    """Parent exception for all Authentication errors."""


class ClientSettingError(ApiError):
    """Pass."""

    def __init__(self, name, value, error, schema):
        """Pass."""
        self.name = name
        self.value = value
        self.error = error
        self.schema = schema

        msg = "{req} setting {n!r} with value of {v!r} {error}, setting schema:\n  {ss}"
        msg = msg.format(
            req="Required" if schema["required"] else "Optional",
            n=name,
            v=value,
            error=error,
            ss=tools.json.dump(schema),
        )
        super(ClientSettingError, self).__init__(msg)


class ResponseError(ApiError):
    """Parent exception for any response error."""

    def __init__(self, response, error="", exc=None, details=True, bodies=True):
        """Constructor.

        Args:
            response (:obj:`requests.Response`):
                Response error was thrown for.
            error (:obj:`str`, optional):
                Error message.

                Defaults to: "".
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.
            bodies (:obj:`bool`, optional):
                Show request and response bodies.

                Defaults to: True.

        """
        self.response = response
        """:obj:`requests.Response`: Response error was thrown for."""

        error = error or "Response error!"
        self.error = error
        """:obj:`str`: Error message."""

        self.exc = exc
        """:obj:`Exception`: Original exception thrown."""

        msgs = []

        if error:
            msgs.append(error)

        if details:
            txt = [
                "code={r.status_code!r}",
                "reason={r.reason!r}",
                "method={r.request.method!r}",
                "url={r.url!r}",
            ]
            txt = tools.join.comma(txt).format(r=response)
            error = "Response details: {}".format(txt)
            msgs.append(error)

        if exc:
            error = "original exception: {}".format(exc)
            msgs.append(error)

        if bodies:
            msgs += [
                "*** request ***",
                tools.json.re_load(response.request.body),
                "*** response ***",
                tools.json.re_load(response.text),
            ]

        msg = tools.join.cr(msgs)

        super(ResponseError, self).__init__(msg)


class JsonInvalid(ResponseError):
    """Error when response has invalid JSON."""

    def __init__(self, response, exc=None, details=True, bodies=True):
        """Constructor.

        Args:
            response (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.

        """
        error = "JSON is not valid in response"
        super(JsonInvalid, self).__init__(
            response=response, error=error, exc=exc, details=details, bodies=bodies
        )


class JsonError(ResponseError):
    """Error when response has error key in JSON."""

    def __init__(self, response, data, exc=None, details=True, bodies=True):
        """Constructor.

        Args:
            response (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.

        """
        has_error = data.get("error")
        has_error_status = data.get("status") == "error"

        error = "JSON has an error message in response"

        if has_error:
            error = "JSON has error='{}' in response".format(has_error)
        elif has_error_status:
            error = "JSON has status='error' in response"

        super(JsonError, self).__init__(
            response=response, error=error, exc=exc, details=details, bodies=bodies
        )


class ClientConnectFailure(ResponseError):
    """Error when response has error key in JSON."""

    def __init__(self, response, adapter, node, exc=None, details=True, bodies=True):
        """Constructor.

        Args:
            response (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.

        """
        error = "Client connectivity failed for adapter {adapter!r} on node {node!r}"
        error = error.format(adapter=adapter, node=node)
        super(ClientConnectFailure, self).__init__(
            response=response, error=error, exc=exc, details=details, bodies=bodies
        )


class ObjectNotFound(ApiError):
    """Error when unable to find an object."""

    def __init__(
        self, value, value_type, object_type, count_total=0, known=None, exc=None
    ):
        """Constructor.

        Args:
            value (:obj:`str`):
                Value used to find object.
            value (:obj:`str`):
                Type of value used to find object.
            object_type (:obj:`str`):
                Type of object searched for.

        """
        self.value = value
        """:obj:`str`: Value used to find object."""

        self.value_type = value_type
        """:obj:`str`: Value type used to find object."""

        self.object_type = object_type
        """:obj:`str`: Type of object searched for."""

        msgs = []

        msg = "Found {c} {obj_type} using {val_type}: {val!r}"
        msg = msg.format(
            c=count_total, val=value, val_type=value_type, obj_type=object_type
        )
        msgs.append(msg)

        if exc:
            msg = " -- original exception: {}"
            msg = msg.format(exc)
            msgs.append(msg)

        if callable(known):
            try:
                known = tools.join.cr(known())
            except Exception as kexc:
                msg = "known callback {} failed {}"
                msg = msg.format(known, kexc)
                msgs.append(msg)

        if known:
            msg = " valids: {}"
            msg = msg.format(known)
            msgs.append(msg)

        msg = tools.join.cr(msgs)
        super(ObjectNotFound, self).__init__(msg)


class TooFewObjectsFound(ObjectNotFound):
    """Error when too many objects found."""

    def __init__(
        self, value, value_type, object_type, count_total, count_min, exc=None
    ):
        """Constructor.

        Args:
            value (:obj:`str`):
                Value used to find object.
            value (:obj:`str`):
                Type of value used to find object.
            object_type (:obj:`str`):
                Type of object searched for.

        """
        self.value = value
        """:obj:`str`: Value used to find object."""

        self.value_type = value_type
        """:obj:`str`: Value type used to find object."""

        self.object_type = object_type
        """:obj:`str`: Type of object searched for."""

        msg = "Expected at least {tmin}, found {tcnt} {obj_type} objects"
        msg += " using {val_type}: {val!r}"
        msg = msg.format(
            val=value,
            val_type=value_type,
            obj_type=object_type,
            tcnt=count_total,
            tmin=count_min,
        )
        msg = "{} -- original exception: {}".format(msg, exc) if exc else msg

        super(ObjectNotFound, self).__init__(msg)


class TooManyObjectsFound(ObjectNotFound):
    """Error when too many objects found."""

    def __init__(
        self, value, value_type, object_type, count_total, count_max, exc=None
    ):
        """Constructor.

        Args:
            value (:obj:`str`):
                Value used to find object.
            value (:obj:`str`):
                Type of value used to find object.
            object_type (:obj:`str`):
                Type of object searched for.

        """
        self.value = value
        """:obj:`str`: Value used to find object."""

        self.value_type = value_type
        """:obj:`str`: Value type used to find object."""

        self.object_type = object_type
        """:obj:`str`: Type of object searched for."""

        msg = "Expected no more than {tmax}, found {tcnt} {obj_type} objects"
        msg += " using {val_type}: {val!r}"
        msg = msg.format(
            val=value,
            val_type=value_type,
            obj_type=object_type,
            tcnt=count_total,
            tmax=count_max,
        )
        msg = "{} -- original exception: {}".format(msg, exc) if exc else msg

        super(ObjectNotFound, self).__init__(msg)


class UnknownError(ObjectNotFound):
    """Pass."""

    def __init__(self, value, known, reason_msg, valid_msg, **kwargs):
        """Constructor."""
        self.value = value
        self.known = known
        self.kwargs = kwargs

        reason = "Unable to find {reason_msg} {v!r}"
        self.reason = reason.format(reason_msg=reason_msg, v=value)

        msg = "{reason}, valid {valid_msg}: {valids}"
        msg = msg.format(
            reason=self.reason, valid_msg=valid_msg, valids=tools.join.cr(known)
        )
        super(ObjectNotFound, self).__init__(msg)


class InvalidCredentials(AuthError):
    """Error on failed login."""

    def __init__(self, auth, exc=None):
        """Constructor.

        Args:
            auth (:obj:`axonius_api_client.models.AuthModel`):
                Authentication method.
            exc (:obj:`Exception`, optional):
                Original Exception, if any.

                Defaults to: None.

        """
        self.auth = auth
        """:obj:`axonius_api_client.models.AuthModel`: Authentication method."""

        self.exc = exc
        """:obj:`Exception`: Original Exception, if any."""

        msg = "Invalid credentials on {auth} -- exception: {exc}"
        msg = msg.format(auth=auth, exc=exc)
        super(InvalidCredentials, self).__init__(msg)


class NotLoggedIn(AuthError):
    """Error when not logged in."""

    def __init__(self, auth):
        """Constructor.

        Args:
            auth (:obj:`axonius_api_client.models.AuthModel`):
                Authentication method.

        """
        self.auth = auth
        """:obj:`axonius_api_client.models.AuthModel`: Authentication method."""

        msg = "Must call login() on {auth}"
        msg = msg.format(auth=auth)
        super(NotLoggedIn, self).__init__(msg)


class AlreadyLoggedIn(AuthError):
    """Error when already logged in."""

    def __init__(self, auth):
        """Constructor.

        Args:
            auth (:obj:`axonius_api_client.models.AuthModel`):
                Authentication method.

        """
        self.auth = auth
        """:obj:`axonius_api_client.models.AuthModel`: Authentication method."""

        msg = "Already logged in on {auth}"
        msg = msg.format(auth=auth)
        super(AlreadyLoggedIn, self).__init__(msg)


class ConnectError(AxonError):
    """Pass."""

    def __init__(self, msg, exc):
        """Pass."""
        self.msg = msg
        self.exc = exc
        super(ConnectError, self).__init__(msg)
