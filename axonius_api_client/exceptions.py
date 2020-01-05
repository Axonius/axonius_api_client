# -*- coding: utf-8 -*-
"""Parent exception and warnings for this package."""
from __future__ import absolute_import, division, print_function, unicode_literals


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
        """Pass."""
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
        """Pass.

        Args:
            added (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.

        """
        from . import tools

        msg = [
            "Connection info: {cnxinfo}",
            "Will not delete connection unless force=True!!",
        ]
        msg = tools.join_cr(obj=msg).format(cnxinfo=cnxinfo)
        super(CnxDeleteForce, self).__init__(msg)


class CnxDeleteFailed(CnxError):
    """Pass."""

    def __init__(self, cnxinfo, response):
        """Pass."""
        from . import tools

        self.cnxinfo = cnxinfo
        self.response = response

        msg = [
            "Connection info: {cnxinfo}",
            "Failed to delete connection!!",
            "Response:{response}",
        ]
        msg = tools.join_cr(obj=msg).format(
            cnxinfo=cnxinfo, response=tools.json_reload(obj=response, error=False)
        )

        super(CnxDeleteFailed, self).__init__(msg)


class CnxDeleteWarning(CnxWarning):
    """Pass."""

    def __init__(self, cnxinfo, sleep):
        """Pass."""
        from . import tools

        msg = ["Connection info: {cnxinfo}", "Will delete connection in {s} seconds!!"]
        msg = tools.join_cr(obj=msg).format(s=sleep, cnxinfo=cnxinfo)

        super(CnxDeleteWarning, self).__init__(msg)


class CnxDeleteFailedWarning(CnxWarning):
    """Pass."""

    def __init__(self, cnxinfo, response):
        """Pass."""
        from . import tools

        self.cnxinfo = cnxinfo
        self.response = response

        msg = [
            "Connection info: {cnxinfo}",
            "Failed to delete connection!!",
            "Response: {response}",
        ]
        msg = tools.join_cr(obj=msg).format(cnxinfo=cnxinfo, response=response)

        super(CnxDeleteFailedWarning, self).__init__(msg)


class CnxRefetchFailure(CnxError):
    """Pass."""

    def __init__(
        self, response, adapter, node, filter_value, filter_method, known=None, **kwargs
    ):
        """Pass.

        Args:
            response (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.

        """
        from . import tools

        self.response = response
        self.adapter = adapter
        self.node = node
        self.known = known
        self.kwargs = kwargs

        if known:
            known = known_cb(known=known, kwargs=kwargs)
            known = tools.join_cr(obj=known, indent="    ")

        msgs = [
            "Failed to find connection",
            "Adapter {!r} on node {!r}".format(adapter, node),
            "Filter value {!r}".format(filter_value),
            "Filter method {}".format(filter_method),
            tools.json_reload(obj=response, error=False),
            "Known connections: {}".format(known),
        ]

        msg = tools.join_cr(obj=msgs)
        super(CnxRefetchFailure, self).__init__(msg)


class CnxCsvWarning(CnxWarning):
    """Pass."""

    def __init__(self, ids_type, ids, name, headers):
        """Pass."""
        msg = "No {ids_type} identifiers {ids} found in CSV file {name} headers {h}"
        msg = msg.format(ids_type=ids_type, ids=ids, name=name, h=headers)

        super(CnxCsvWarning, self).__init__(msg)


class CnxConnectFailure(CnxError):
    """Error when response has error key in JSON."""

    def __init__(self, response, adapter, node):
        """Pass.

        Args:
            response (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.

        """
        from . import tools

        self.response = response
        self.adapter = adapter
        self.node = node

        msg = "Connection test failed for adapter {a!r} on node {n!r}:\n{r}"
        msg = msg.format(
            a=adapter, n=node, r=tools.json_reload(obj=response, error=False)
        )

        super(CnxConnectFailure, self).__init__(msg)


class CnxSettingError(CnxError):
    """Pass."""

    def __init__(self, name, value, schema, adapter, error):
        """Pass."""
        from . import tools

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

        msg = tools.join_cr(obj=msg).format(
            a=adapter["name"],
            an=adapter["node_name"],
            req="required" if schema["required"] else "optional",
            n=name,
            v=value,
            error=error,
            ss=tools.json_dump(obj=schema, error=False),
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
        from . import tools

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
        examples = tools.join_cr(obj=[format(x) for x in examples])

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
        """Pass.

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
        from . import tools

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
            txt = tools.join_comma(obj=txt).format(r=response)
            error = "Response details: {}".format(txt)
            msgs.append(error)

        if exc:
            error = "original exception: {}".format(exc)
            msgs.append(error)

        if bodies:
            msgs += [
                "*** request ***",
                tools.json_reload(obj=response.request.body, error=False),
                "*** response ***",
                tools.json_reload(obj=response.text, error=False),
            ]

        msg = tools.join_cr(obj=msgs)

        super(ResponseError, self).__init__(msg)


class ResponseNotOk(ResponseError):
    """Error when response has invalid JSON."""


class JsonInvalid(ResponseError):
    """Error when response has invalid JSON."""

    def __init__(self, response, exc=None, details=True, bodies=True):
        """Pass.

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
        """Pass.

        Args:
            response (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.

        """
        from . import tools

        if isinstance(data, dict):
            data = ["{}: {}".format(k, v) for k, v in data.items()]
            data = tools.join_cr(obj=data, indent="    ")

        error = "Found error in response JSON: {d}"
        error = error.format(d=data)

        super(JsonError, self).__init__(
            response=response, error=error, exc=exc, details=details, bodies=bodies
        )


class ValueNotFound(ApiError):
    """Pass."""

    def __init__(
        self,
        value,
        value_msg,
        known=None,
        known_msg=None,
        exc=None,
        match_type="equals",
        # fmt: off
        **kwargs
        # fmt: on
    ):
        """Pass."""
        from . import tools

        self.value = value
        self.known = known
        self.kwargs = kwargs
        self.exc = exc

        msgs = []

        if exc:
            msg = "Original exception: {exc}".format(exc=exc)
            msgs.append(msg)

        msg = "Unable to find {vm} that {mt} value {v!r}"
        msg = msg.format(vm=value_msg, v=value, mt=match_type)
        msgs.append(msg)

        if known:
            known = known_cb(known=known, kwargs=kwargs)

            msg = "Valid {known_msg}: {v}"
            msg = msg.format(
                known_msg=known_msg, v=tools.join_cr(obj=known, indent="    ")
            )
            msgs.append(msg)

        msg = tools.join_cr(obj=msgs)
        super(ApiError, self).__init__(msg)


class InvalidCredentials(AuthError):
    """Error on failed login."""

    def __init__(self, auth, exc=None):
        """Pass.

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
        """Pass.

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
        """Pass.

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


def known_cb(known, kwargs=None):
    """Pass."""
    kwargs = kwargs or {}

    if callable(known):
        try:
            known = known(**kwargs)
        except Exception as exc:
            msg = "known callback {cb} with kwargs {kw} failed with exception {exc}"
            known = [msg.format(cb=known, kw=kwargs, exc=exc)]

    return known
