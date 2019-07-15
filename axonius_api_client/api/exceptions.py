# -*- coding: utf-8 -*-
"""API errors."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .. import exceptions
from .. import tools


class ApiError(exceptions.PackageError):
    """Parent exception for all API errors."""


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

        if details:
            txt = [
                "code={r.status_code!r}",
                "reason={r.reason!r}",
                "method={r.request.method!r}",
                "url={r.url!r}",
            ]

            txt = "({})".format(", ".join(txt).format(r=response))
            error = "{} Response details {}".format(error, txt)

        error = "{} (original exception: {})".format(error, exc) if exc else error

        msgs.append(error)

        if bodies:
            req_txt = tools.json_pretty(response.request.body)
            resp_txt = tools.json_pretty(response.request.body)
            msgs += ["*** request ***", req_txt, "*** response ***", resp_txt]

        msg = msgs[0] if len(msgs) == 1 else "\n".join(msgs)

        super(ResponseError, self).__init__(msg)


class InvalidJson(ResponseError):
    """Error when response has invalid JSON."""

    def __init__(self, response, exc=None):
        """Constructor.

        Args:
            response (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`, optional):
                Original exception thrown.

                Defaults to: None.

        """
        error = "Invalid JSON in response"
        super(InvalidJson, self).__init__(response=response, error=error, exc=exc)


class ObjectNotFound(ApiError):
    """Error when unable to find an object."""

    def __init__(self, value, value_type, object_type, exc=None):
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

        msg = "Unable to find {obj_type} using {val_type}: {val!r}"
        msg = msg.format(val=value, val_type=value_type, obj_type=object_type)
        msg = "{} -- original exception: {}".format(msg, exc) if exc else msg

        super(ObjectNotFound, self).__init__(msg)


class TooFewObjectsFound(ApiError):
    """Error when too many objects found."""

    def __init__(
        self, value, value_type, object_type, row_count_total, row_count_min, exc=None
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
            tcnt=row_count_total,
            tmin=row_count_min,
        )
        msg = "{} -- original exception: {}".format(msg, exc) if exc else msg

        super(TooFewObjectsFound, self).__init__(msg)


class TooManyObjectsFound(ApiError):
    """Error when too many objects found."""

    def __init__(
        self, value, value_type, object_type, row_count_total, row_count_max, exc=None
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
            tcnt=row_count_total,
            tmax=row_count_max,
        )
        msg = "{} -- original exception: {}".format(msg, exc) if exc else msg

        super(TooManyObjectsFound, self).__init__(msg)


class UnknownAdapterName(ApiError):
    """Error when unable to find an adapter name."""

    def __init__(self, name, known_names):
        """Constructor.

        Args:
            name (:obj:`str`):
                Name of adapter that was not found.
            known_names (:obj:`list` of :obj:`str`):
                Names of adapters that exist.

        """
        self.name = name
        """:obj:`str`: Name of adapter that was not found."""

        self.known_names = known_names
        """:obj:`list` of :obj:`str`: Names of adapters that exist."""

        msg = "Unable to find adapter {name!r}, valid adapters: {names}"
        msg = msg.format(name=name, names=known_names)

        super(UnknownAdapterName, self).__init__(msg)


class UnknownFieldName(ApiError):
    """Error when unable to find a generic or adapter field name."""

    def __init__(self, name, adapter, known_names):
        """Constructor.

        Args:
            name (:obj:`str`):
                Name of field that was not found.
            adapter (:obj:`str`):
                Name of adapter that field was being looked for.
            known_names (:obj:`list` of :obj:`str`):
                Names of fields that exist.

        """
        self.name = name
        """:obj:`str`: Name of field that was not found."""

        self.known_names = known_names
        """:obj:`list` of :obj:`str`: Names of fields that exist."""

        self.adapter = adapter
        """:obj:`str`: Name of adapter that field was being looked for."""

        msg = "Unable to find {adapter} field {field!r}, valid fields: {names}"
        msg = msg.format(adapter=adapter, field=name, names=known_names)

        super(UnknownFieldName, self).__init__(msg)
