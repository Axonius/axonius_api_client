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


class SavedQueryNotFound(PackageError):
    """Error when unable to find a saved query."""

    def __init__(self, query):
        """Constructor.

        Args:
            query (:obj:`str`):
                Filter used to find saved queries.

        """
        self.query = query
        """:obj:`str`: ID of device not found.."""

        msg = "Unable to find saved query using filter {query!r}"
        msg = msg.format(query=query)

        super(SavedQueryNotFound, self).__init__(msg)


class ObjectNotFound(PackageError):
    """Error when unable to find an object by ID."""

    def __init__(self, id):
        """Constructor.

        Args:
            id (:obj:`str`):
                ID of object not found.

        """
        self.id = id
        """:obj:`str`: ID of object not found.."""

        msg = "Unable to find object by id {id!r}"
        msg = msg.format(id=id)

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
