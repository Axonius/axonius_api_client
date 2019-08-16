# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class ApiModel(object):
    """API client for Axonius REST API."""

    @abc.abstractproperty
    def _router(self):
        """Router for this API client.

        Returns:
            :obj:`axonius_api_client.api.routers.Router`

        """
        raise NotImplementedError  # pragma: no cover


@six.add_metaclass(abc.ABCMeta)
class ApiModelUserDevice(ApiModel):
    """API client for Axonius REST API."""

    @abc.abstractproperty
    def _default_fields(self):
        """Fields to set as default for methods with fields as kwargs.

        Returns:
            :obj:`dict`

        """
        raise NotImplementedError  # pragma: no cover


@six.add_metaclass(abc.ABCMeta)
class AuthModel(object):
    """Abstract base class for all Authentication methods."""

    @abc.abstractmethod
    def login(self):
        """Login to API."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def logout(self):
        """Logout from API."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def check_login(self):
        """Throw exc if not login.

        Raises:
            :exc:`exceptions.NotLoggedIn`

        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractproperty
    def http_client(self):
        """Get HttpClient object.

        Returns:
            :obj:`axonius_api_client.http.interfaces.HttpClient`

        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractproperty
    def is_logged_in(self):
        """Check if login has been called.

        Returns:
            :obj:`bool`

        """
        raise NotImplementedError  # pragma: no cover
