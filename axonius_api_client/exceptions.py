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


class DeviceIDNotFound(PackageError):
    """Error when unable to find a device by ID."""

    def __init__(self, id):
        """Constructor.

        Args:
            id (:obj:`str`):
                ID of device not found.

        """
        self.id = id
        """:obj:`str`: ID of device not found.."""

        msg = "Unable to find device by id {id!r}"
        msg = msg.format(id=id)

        super(DeviceIDNotFound, self).__init__(msg)


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

    def __init__(self, name, known_names, adapter=None):
        """Constructor.

        Args:
            name (:obj:`str`):
                Name of field that was not found.
            known_names (:obj:`list` of :obj:`str`):
                Names of fields that exist.
            adapter (:obj:`str`, optional):
                Name of adapter that field was being looked for. If None, the field
                is considered a generic field.

                Defaults to: None.

        """
        self.name = name
        """:obj:`str`: Name of field that was not found."""

        self.known_names = known_names
        """:obj:`list` of :obj:`str`: Names of fields that exist."""

        self.adapter = adapter
        """:obj:`str`: Name of adapter that field was being looked for."""

        self.field_type = adapter if adapter else "generic"
        """:obj:`str`: Type of field being looked for, generic or adapter specific."""

        msg = "Unable to find a {field_type} field {field!r}, valid fields: {names}"
        msg = msg.format(field_type=self.field_type, field=name, names=known_names)

        super(UnknownFieldName, self).__init__(msg)
