# -*- coding: utf-8 -*-
"""Parent exception and warnings for this package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class PackageError(Exception):
    """Parent exception for all package errors."""


class PackageWarning(Warning):
    """Parent warning all package warnings."""


class InvalidCredentials(PackageError):
    """Error on failed login."""


class MustLogin(PackageError):
    """Error when not logged in."""

    def __init__(self, auth):
        self.auth = auth
        msg = "{auth} is not logged in, use login()".format(auth=auth)
        super(MustLogin, self).__init__(msg)


class UnknownAdapterName(PackageError):
    """Error when unable to find an adapter name."""

    def __init__(self, name, known_names):
        self.name = name
        self.known_names = known_names

        msg = "Unable to find adapter {name!r}, valid adapters: {names}"
        msg = msg.format(name=name, names=known_names)

        super(UnknownAdapterName, self).__init__(msg)


class UnknownFieldName(PackageError):
    """Error when unable to find an adapter name."""

    def __init__(self, name, known_names, adapter_name=None):
        self.name = name
        self.known_names = known_names
        self.adapter_name = adapter_name
        self.field_type = adapter_name if adapter_name else "generic"

        msg = "Unable to find a {field_type} field {field!r}, valid fields: {names}"
        msg = msg.format(field_type=self.field_type, field=name, names=known_names)

        super(UnknownFieldName, self).__init__(msg)
