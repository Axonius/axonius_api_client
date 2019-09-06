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


class BetaWarning(AxonWarning):
    """Pass."""

    def __init__(self, obj):
        """Constructor."""
        msg = "Object {obj} is considered **BETA** status! Here be dragons..."
        msg = msg.format(obj=obj)

        super(AxonWarning, self).__init__(msg)


class ToolsError(AxonError):
    """Parent exception for all tools errors."""


class AuthError(AxonError):
    """Parent exception for all Authentication errors."""


class HttpError(AxonError):
    """Parent exception for all Authentication errors."""


class CnxError(ApiError):
    """Pass."""


class CnxWarning(ApiWarning):
    """Pass."""


class CnxDeleteForce(CnxError):
    """Pass."""

    def __init__(self, cnxinfo):
        """Constructor.

        Args:
            added (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.

        """
        msg = [
            "Connection info: {cnxinfo}",
            "Will not delete connection unless force=True!!",
        ]
        msg = tools.join.cr(msg).format(cnxinfo=cnxinfo)
        super(CnxDeleteForce, self).__init__(msg)


class CnxDeleteFailed(CnxError):
    """Pass."""

    def __init__(self, cnxinfo, response):
        """Constructor."""
        self.cnxinfo = cnxinfo
        self.response = response

        msg = [
            "Connection info: {cnxinfo}",
            "Failed to delete connection!!",
            "Response:{response}",
        ]
        msg = tools.join.cr(msg).format(
            cnxinfo=cnxinfo, response=tools.json.re_load(response)
        )

        super(CnxDeleteFailed, self).__init__(msg)


class CnxDeleteWarning(CnxWarning):
    """Pass."""

    def __init__(self, cnxinfo, sleep):
        """Constructor."""
        msg = ["Connection info: {cnxinfo}", "Will delete connection in {s} seconds!!"]
        msg = tools.join.cr(msg).format(s=sleep, cnxinfo=cnxinfo)

        super(CnxDeleteWarning, self).__init__(msg)


class CnxDeleteFailedWarning(CnxWarning):
    """Pass."""

    def __init__(self, cnxinfo, response):
        """Constructor."""
        self.cnxinfo = cnxinfo
        self.response = response

        msg = [
            "Connection info: {cnxinfo}",
            "Failed to delete connection!!",
            "Response: {response}",
        ]
        msg = tools.join.cr(msg).format(cnxinfo=cnxinfo, response=response)

        super(CnxDeleteFailedWarning, self).__init__(msg)


class CnxRefetchFailure(CnxError):
    """Pass."""

    def __init__(self, response, adapter, node):
        """Constructor.

        Args:
            response (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.

        """
        self.response = response
        self.adapter = adapter
        self.node = node

        msg = "Failed to find connection for adapter {a!r} on node {n!r}:\n  {r}"
        msg = msg.format(a=adapter, n=node, r=tools.json.re_load(response))

        super(CnxRefetchFailure, self).__init__(msg)


class CnxCsvWarning(CnxWarning):
    """Pass."""

    def __init__(self, ids_type, ids, name, headers):
        """Constructor."""
        msg = "No {ids_type} identifiers {ids} found in CSV file {name} headers {h}"
        msg = msg.format(ids_type=ids_type, ids=ids, name=name, h=headers)

        super(CnxCsvWarning, self).__init__(msg)


class CnxConnectFailure(CnxError):
    """Error when response has error key in JSON."""

    def __init__(self, response, adapter, node):
        """Constructor.

        Args:
            response (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.

        """
        self.response = response
        self.adapter = adapter
        self.node = node

        msg = "Connection test failed for adapter {a!r} on node {n!r}:\n{r}"
        msg = msg.format(a=adapter, n=node, r=tools.json.re_load(response))

        super(CnxConnectFailure, self).__init__(msg)


class CnxSettingError(CnxError):
    """Pass."""

    def __init__(self, name, value, schema, adapter, error):
        """Pass."""
        self.name = name
        self.value = value
        self.schema = schema
        self.adapter = adapter
        self.error = error

        msg = [
            "Error with {req} setting {n!r} on adapter {a!r} on node {an!r}",
            "Supplied value of {v!r}",
            "Setting schema:",
            "{ss}",
            "Error: {error}",
        ]

        msg = tools.join.cr(msg).format(
            a=adapter["name"],
            an=adapter["node_name"],
            req="required" if schema["required"] else "optional",
            n=name,
            v=value,
            error=error,
            ss=tools.json.dump(schema),
        )

        super(CnxSettingError, self).__init__(msg)


class CnxSettingMissing(CnxSettingError):
    """Pass."""

    def __init__(self, name, value, schema, adapter):
        """Pass."""
        error = "Setting {n!r} was not supplied and no default value defined"
        error = error.format(n=name)

        super(CnxSettingMissing, self).__init__(
            name=name, value=value, schema=schema, error=error, adapter=adapter
        )


class CnxSettingFileMissing(CnxSettingError):
    """Pass."""

    def __init__(self, name, value, schema, adapter):
        """Pass."""
        examples = [
            {
                name: {
                    "uuid": "uuid of already uploaded file",
                    "filename": "name of already uploaded file",
                }
            },
            {
                name: {
                    "filename": "name of file to use when uploading file",
                    "filecontent": "content of file to upload",
                    "filecontent_type": "optional mime type",
                }
            },
            {
                name: {
                    "filepath": "path of file to upload",
                    "filecontent_type": "optional mime type",
                }
            },
        ]
        examples = tools.join.cr([format(x) for x in examples])

        error = "File setting {n!r} with value {v!r} is invalid, examples: {ex}"
        error = error.format(n=name, v=value, ex=examples)

        super(CnxSettingFileMissing, self).__init__(
            name=name, value=value, schema=schema, error=error, adapter=adapter
        )


class CnxSettingInvalidType(CnxSettingError):
    """Pass."""

    def __init__(self, name, value, schema, mustbe, adapter):
        """Pass."""
        self.mustbe = mustbe

        error = "Invalid type supplied {t!r}, must be type {mt!r}"
        error = error.format(t=type(value).__name__, mt=mustbe)

        super(CnxSettingInvalidType, self).__init__(
            name=name, value=value, schema=schema, error=error, adapter=adapter
        )


class CnxSettingInvalidChoice(CnxSettingError):
    """Pass."""

    def __init__(self, name, value, enum, schema, adapter):
        """Pass."""
        self.enum = enum

        error = "Invalid value {v!r}, must be one of {e}"
        error = error.format(v=value, e=enum)

        super(CnxSettingInvalidChoice, self).__init__(
            name=name, value=value, schema=schema, error=error, adapter=adapter
        )


class CnxSettingUnknownType(CnxSettingError):
    """Pass."""

    def __init__(self, name, value, type_str, schema, adapter):
        """Pass."""
        self.type_str = type_str

        error = "Unknown connection setting type {t!r} in schema"
        error = error.format(t=type_str)

        super(CnxSettingUnknownType, self).__init__(
            name=name, value=value, schema=schema, error=error, adapter=adapter
        )


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


class ResponseCodeNot200(ResponseError):
    """Error when response has invalid JSON."""


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

    def __init__(self, response, data, exc=None, details=True, bodies=False):
        """Constructor.

        Args:
            response (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.

        """
        if tools.is_type.dict(data):
            data = ["{}: {}".format(k, v) for k, v in data.items()]
            data = tools.join.cr(data, indent="    ")

        error = "Found error in response JSON: {d}"
        error = error.format(d=data)

        super(JsonError, self).__init__(
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

        known = known_cb(known)

        if known:
            msg = " valids: {v}"
            msg = msg.format(v=tools.join.cr(known))
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


class ValueNotFound(ObjectNotFound):
    """Pass."""

    def __init__(self, value, value_msg, known, known_msg, **kwargs):
        """Constructor."""
        self.value = value
        self.known = known
        self.kwargs = kwargs

        msgs = []

        msg = "Unable to find {value_msg} {v!r}"
        msg = msg.format(value_msg=value_msg, v=value)
        msgs.append(msg)

        known = known_cb(known)

        msg = "Valid {known_msg}: {v}"
        msg = msg.format(known_msg=known_msg, v=tools.join.cr(known, indent="    "))
        msgs.append(msg)

        msg = tools.join.cr(msgs)
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


def known_cb(known):
    """Pass."""
    if callable(known):
        try:
            known = known()
        except Exception as kexc:  # pragma: no cover
            known = ["known callback {} failed {}".format(known, kexc)]
    return known
