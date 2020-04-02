# -*- coding: utf-8 -*-
"""Exceptions and warnings."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# WARNINGS


class AxonWarning(Warning):
    """Warnings for :mod:`axonius_api_client`."""


class ApiWarning(AxonWarning):
    """Warnings for :mod:`.api`."""


class BetaWarning(AxonWarning):
    """Warn that an object is in BETA status."""

    def __init__(self, obj):
        """Throw a warning that an object is in BETA status.

        Args:
            obj (:obj:`object`): object to include str of in warning msg
        """
        msg = "Object {obj} is considered **BETA** status! Here be dragons..."
        msg = msg.format(obj=obj)

        super(AxonWarning, self).__init__(msg)


class CsvIdentifierWarning(ApiWarning):
    """Warn when CSV has no strong identifier columns."""

    def __init__(self, ids_type, ids, name, headers):
        """Warn when CSV has no strong identifier columns.

        Args:
            ids_type (:obj:`str`): type of csv being checked
            ids (:obj:`list` of :obj:`str`): list of strong identifiers for this type of
                csv
            name (:obj:`str`): name of csv file
            headers (:obj:`object`): columns in csv
        """
        msg = "No {ids_type} identifiers {ids} found in CSV file {name} headers {h}"
        msg = msg.format(ids_type=ids_type, ids=ids, name=name, h=headers)

        super(CsvIdentifierWarning, self).__init__(msg)


class CnxDeleteWarning(ApiWarning):
    """Warn that a connection is about to be deleted."""

    def __init__(self, cnxinfo, sleep):
        """Warn that a connection is about to be deleted.

        Args:
            cnxinfo (:obj:`str`): info about connection
            sleep (:obj:`int`): how long until the connection will be deleted
        """
        from . import tools

        msg = ["Connection info: {cnxinfo}", "Will delete connection in {s} seconds!!"]
        msg = tools.join_cr(obj=msg).format(s=sleep, cnxinfo=cnxinfo)

        super(CnxDeleteWarning, self).__init__(msg)


class CnxDeleteFailedWarning(ApiWarning):
    """Warn when deleting a connection had an error and error=False."""

    def __init__(self, cnxinfo, response):
        """Warn when deleting a connection had an error and error=False.

        Args:
            cnxinfo (:obj:`str`): info about connection
            response (:obj:`str`): text returned from request to delete the connection
        """
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


# EXCEPTIONS
class AxonError(Exception):
    """Errors for :mod:`axonius_api_client`."""


class ApiError(AxonError):
    """Errors for :mod:`.api`."""


class ToolsError(AxonError):
    """Errors for :mod:`.tools`."""


class AuthError(AxonError):
    """Errors for :mod:`.auth`."""


class HttpError(AxonError):
    """Errors for :mod:`.http`."""


class CnxError(ApiError):
    """Errors for :obj:`.api.adapters.Cnx`."""


class CnxDeleteForce(CnxError):
    """Error when deleting a connection and force=False."""

    def __init__(self, cnxinfo):
        """Error when deleting a connection and force=False.

        Args:
            cnxinfo (:obj:`str`): info about connection
        """
        from . import tools

        msg = [
            "Connection info: {cnxinfo}",
            "Will not delete connection unless force=True!!",
        ]
        msg = tools.join_cr(obj=msg).format(cnxinfo=cnxinfo)
        super(CnxDeleteForce, self).__init__(msg)


class CnxDeleteFailed(CnxError):
    """Error when deleting a connection had an error and error=True."""

    def __init__(self, cnxinfo, response):
        """Error when deleting a connection had an error and error=True.

        Args:
            cnxinfo (:obj:`str`): info about connection
            response (:obj:`str`): text returned from request to delete the connection
        """
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


class CnxRefetchFailure(CnxError):
    """Error when an updated connection can not be re-fetched."""

    def __init__(
        self, response, adapter, node, filter_value, filter_method, known=None, **kwargs
    ):
        """Error when an updated connection can not be re-fetched.

        Args:
            response (:obj:`requests.Response`): response from last refetch attempt
            adapter (:obj:`str`): name of adapter for refetch
            node (:obj:`str`): node name of adapter for refetch
            filter_value (:obj:`str`): value being passed to filter method
            filter_method (:obj:`object`): method being used to find connection
            known (:obj:`object`, optional): callback method to get known connections
            **kwargs: passed to known
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


class CnxConnectFailure(CnxError):
    """Error when adding/updating/checking a connection fails the connection test."""

    def __init__(self, response, adapter, node):
        """Error when adding/updating/checking a connection fails the connection test.

        Args:
            response (:obj:`str`): text from response
            adapter (:obj:`str`): name of adapter
            node (:obj:`str`): node name of adapter
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
    """Errors when parsing settings."""

    def __init__(self, name, value, schema, adapter, error):
        """Errors when parsing settings.

        Args:
            name (:obj:`str`): setting name
            value (:obj:`object`): value supplied for setting
            schema (:obj:`dict`): metadata for this setting
            adapter (:obj:`dict`): metadata of adapter for this connection
            error (:obj:`str`): error message from subclassed exception
        """
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
    """Error when no value supplied for a required setting."""

    def __init__(self, name, value, schema, adapter):
        """Error when no value supplied for a required setting.

        Args:
            name (:obj:`str`): setting name
            value (:obj:`object`): value supplied for setting
            schema (:obj:`dict`): metadata for this setting
            adapter (:obj:`dict`): metadata of adapter for this connection
        """
        error = "Setting {n!r} was not supplied and no default value defined"
        error = error.format(n=name)

        super(CnxSettingMissing, self).__init__(
            name=name, value=value, schema=schema, error=error, adapter=adapter
        )


class CnxSettingFileMissing(CnxSettingError):
    """Error when supplied value is invalid for a file-type setting."""

    def __init__(self, name, value, schema, adapter):
        """Error when supplied value is invalid for a file-type setting.

        Args:
            name (:obj:`str`): setting name
            value (:obj:`object`): value supplied for setting
            schema (:obj:`dict`): metadata for this setting
            adapter (:obj:`dict`): metadata of adapter for this connection
        """
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
    """Error when supplied value is the wrong type for a setting."""

    def __init__(self, name, value, schema, mustbe, adapter):
        """Error when supplied value is the wrong type for a setting.

        Args:
            name (:obj:`str`): setting name
            value (:obj:`object`): value supplied for setting
            schema (:obj:`dict`): metadata for this setting
            mustbe (:obj:`object`): the type the value should be
            adapter (:obj:`dict`): metadata of adapter for this connection
        """
        self.mustbe = mustbe

        error = "Invalid type supplied {t!r}, must be type {mt!r}"
        error = error.format(t=type(value).__name__, mt=mustbe)

        super(CnxSettingInvalidType, self).__init__(
            name=name, value=value, schema=schema, error=error, adapter=adapter
        )


class CnxSettingInvalidChoice(CnxSettingError):
    """Error when supplied value is not a valid choice for an enum-type setting."""

    def __init__(self, name, value, enum, schema, adapter):
        """Error when supplied value is not a valid choice for an enum-type setting.

        Args:
            name (:obj:`str`): setting name
            value (:obj:`object`): value supplied for setting
            schema (:obj:`dict`): metadata for this setting
            enum (:obj:`list` of :obj:`str`): valid values
            adapter (:obj:`dict`): metadata of adapter for this connection
        """
        self.enum = enum

        error = "Invalid value {v!r}, must be one of {e}"
        error = error.format(v=value, e=enum)

        super(CnxSettingInvalidChoice, self).__init__(
            name=name, value=value, schema=schema, error=error, adapter=adapter
        )


class CnxSettingUnknownType(CnxSettingError):
    """Error when a schema for a setting has a type that is not known."""

    def __init__(self, name, value, type_str, schema, adapter):
        """Error when a schema for a setting has a type that is not known.

        Args:
            name (:obj:`str`): setting name
            value (:obj:`object`): value supplied for setting
            type_str (:obj:`str`): the type that was not known
            schema (:obj:`dict`): metadata for this setting
            adapter (:obj:`dict`): metadata of adapter for this connection
        """
        self.type_str = type_str

        error = "Unknown setting type {t!r} in schema"
        error = error.format(t=type_str)

        super(CnxSettingUnknownType, self).__init__(
            name=name, value=value, schema=schema, error=error, adapter=adapter
        )


class ResponseError(ApiError):
    """Errors when checking responses."""

    def __init__(self, response, error="", exc=None, details=True, bodies=True):
        """Errors when checking responses.

        Args:
            response (:obj:`requests.Response`): response obj error was thrown for
            error (:obj:`str`, optional): default ``""`` - error message from
                subclassed exception
            exc (:obj:`Exception`, optional): default ``None`` - original exc thrown
            details (:obj:`bool`, optional): default ``True`` -

                * if ``True`` include bodie in exc str
                * if ``False`` do not include bodies  in exc str
            bodies (:obj:`bool`, optional): default ``True`` -

                * if ``True`` include response details in exc str
                * if ``False`` do not include response details in exc str
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
    """Error if response has a status code that is an error and error_status is True."""


class JsonInvalid(ResponseError):
    """Error when response has invalid JSON."""

    def __init__(self, response, exc=None, details=True, bodies=True):
        """Error when response has invalid JSON.

        Args:
            response (:obj:`requests.Response`): response obj error was thrown for
            exc (:obj:`Exception`, optional): default ``None`` - original exc thrown
            details (:obj:`bool`, optional): default ``True`` -

                * if ``True`` include bodie in exc str
                * if ``False`` do not include bodies  in exc str
            bodies (:obj:`bool`, optional): default ``True`` -

                * if ``True`` include response details in exc str
                * if ``False`` do not include response details in exc str
        """
        error = "JSON is not valid in response"
        super(JsonInvalid, self).__init__(
            response=response, error=error, exc=exc, details=details, bodies=bodies
        )


class JsonError(ResponseError):
    """Error when JSON has key:error that is not empty or key:status=error."""

    def __init__(self, response, data, exc=None, details=True, bodies=False):
        """Error when JSON has key:error that is not empty or key:status=error.

        Args:
            response (:obj:`requests.Response`): response obj error was thrown for
            data (:obj:`object`): JSON object from response
            exc (:obj:`Exception`, optional): default ``None`` - original exc thrown
            details (:obj:`bool`, optional): default ``True`` -

                * if ``True`` include bodie in exc str
                * if ``False`` do not include bodies  in exc str
            bodies (:obj:`bool`, optional): default ``True`` -

                * if ``True`` include response details in exc str
                * if ``False`` do not include response details in exc str
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
    """Error when a value is not found."""

    def __init__(
        self,
        value,
        value_msg,
        known=None,
        known_msg=None,
        exc=None,
        match_type="equals",
        **kwargs
    ):
        """Error when a value is not found.

        Args:
            value (:obj:`object`): value that is being searched for
            value_msg (:obj:`str`): explanation of what is being searched for
            known (:obj:`object`, optional): default ``None`` -
                callback method to get known values
            known_msg (:obj:`str`, optional): default ``None`` -
                explanation of what known values are
            exc (:obj:`Exception`, optional): default ``None`` -
                original exc thrown
            match_type (:obj:`str`, optional): default ``"equals"`` -
                operator being used in search
            **kwargs: passed to known callback
        """
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
    """Error when credentials are invalid."""

    def __init__(self, auth, exc=None):
        """Error when credentials are invalid.

        Args:
            auth (:obj:`.auth.Model`): auth method
            exc (:obj:`Exception`, optional): default ``None`` - original exc thrown
        """
        self.auth = auth
        """:obj:`.auth.Model`: auth method"""

        self.exc = exc
        """:obj:`Exception`: Original Exception, if any."""

        msg = "Invalid credentials on {auth} -- exception: {exc}"
        msg = msg.format(auth=auth, exc=exc)
        super(InvalidCredentials, self).__init__(msg)


class NotLoggedIn(AuthError):
    """Error when not logged in."""

    def __init__(self, auth):
        """Error when not logged in.

        Args:
            auth (:obj:`.auth.Model`): auth method
        """
        self.auth = auth
        """:obj:`.auth.Model`: auth method"""

        msg = "Must call login() on {auth}"
        msg = msg.format(auth=auth)
        super(NotLoggedIn, self).__init__(msg)


class AlreadyLoggedIn(AuthError):
    """Error when already logged in."""

    def __init__(self, auth):
        """Error when already logged in.

        Args:
            auth (:obj:`.auth.Model`): auth method
        """
        self.auth = auth
        """:obj:`.auth.Model`: auth method"""

        msg = "Already logged in on {auth}"
        msg = msg.format(auth=auth)
        super(AlreadyLoggedIn, self).__init__(msg)


class ConnectError(AxonError):
    """Error in :obj:`.connect.Connect`."""

    def __init__(self, msg, exc):
        """Error in :obj:`.connect.Connect`.

        Args:
            msg (:obj:`str`): msg to include in exc
            exc (:exc:`Exception`): original exc thrown
        """
        self.msg = msg
        self.exc = exc
        super(ConnectError, self).__init__(msg)


class StopPaging(AxonError):
    """Exception thrown when paging should be stopped."""


def known_cb(known, kwargs=None):
    """Run a callback to get a list of known values.

    Args:
        known (:obj:`object`): callback to run
        kwargs (:obj:`dict`, optional): default ``None`` - kwargs to pass to known

    Returns:
        :obj:`list` of :obj:`str`: known values returned from callback
    """
    kwargs = kwargs or {}

    if callable(known):
        try:
            known = known(**kwargs)
        except Exception as exc:
            msg = "known callback {cb} with kwargs {kw} failed with exception {exc}"
            known = [msg.format(cb=known, kw=kwargs, exc=exc)]

    return known
