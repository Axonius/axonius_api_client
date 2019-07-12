# -*- coding: utf-8 -*-
"""Parent exception and warnings for this package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json


def json_pretty(text):
    """Pass."""
    try:
        return json.dumps(json.loads(text), indent=2)
    except Exception:
        return text or ""


class PackageError(Exception):
    """Parent exception for all package errors."""


class PackageWarning(Warning):
    """Parent warning all package warnings."""


class InvalidCredentials(PackageError):
    """Error on failed login."""

    def __init__(self, auth, exc=None):
        """Constructor.

        Args:
            auth (:obj:`axonius_api_client.models.AuthBase`):
                Authentication method.
            exc (:obj:`Exception`, optional):
                Original Exception, if any.

                Defaults to: None.

        """
        self.auth = auth
        """:obj:`axonius_api_client.models.AuthBase`: Authentication method."""

        self.exc = exc
        """:obj:`Exception`: Original Exception, if any."""

        msg = "Invalid credentials on {auth}"
        msg += "-- exception: {exc}" if exc else ""
        msg = msg.format(auth=auth, exc=exc)
        super(InvalidCredentials, self).__init__(msg)


class NotLoggedIn(PackageError):
    """Error when not logged in."""

    def __init__(self, auth):
        """Constructor.

        Args:
            auth (:obj:`axonius_api_client.models.AuthBase`):
                Authentication method.

        """
        self.auth = auth
        """:obj:`axonius_api_client.models.AuthBase`: Authentication method."""

        msg = "Must call login() on {auth}"
        msg = msg.format(auth=auth)
        super(NotLoggedIn, self).__init__(msg)


class AlreadyLoggedIn(PackageError):
    """Error when already logged in."""

    def __init__(self, auth):
        """Constructor.

        Args:
            auth (:obj:`axonius_api_client.models.AuthBase`):
                Authentication method.

        """
        self.auth = auth
        """:obj:`axonius_api_client.models.AuthBase`: Authentication method."""

        msg = "Already logged in on {auth}"
        msg = msg.format(auth=auth)
        super(AlreadyLoggedIn, self).__init__(msg)


class ResponseError(PackageError):
    """Error when response.raise_for_error."""

    def __init__(self, response, exc):
        """Constructor.

        Args:
            response (:obj:`requests.Response`):
                Response error was thrown for.
            exc (:obj:`Exception`):
                Original exception thrown.

        """
        self.response = response
        """:obj:`requests.Response`: Response error was thrown for."""

        self.exc = exc
        """:obj:`Exception: Original exception thrown."""

        msg = [
            "Error in {response}: {exc}".format(response=response, exc=exc),
            "*** request_text ***",
            json_pretty(response.request.body),
            "*** response text ***",
            json_pretty(response.text),
        ]
        msg = "\n".join(msg)

        super(ResponseError, self).__init__(msg)


class ObjectNotFound(PackageError):
    """Error when unable to find an object."""

    def __init__(self, value, value_type, object_type):
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

        msg = "Unable to find {object_type} using {value_type}: {value!r}"
        msg = msg.format(value=value, value_type=value_type, object_type=object_type)

        super(ObjectNotFound, self).__init__(msg)


class UnknownAdapterName(PackageError):
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


class UnknownFieldName(PackageError):
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
