# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import logging

import six

from . import exceptions

LOG = logging.getLogger(__name__)


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

    def __init__(self, auth):
        """Constructor.

        Args:
            auth (:obj:`AuthModel`):
                Authentication object.

        """
        self._log = LOG.getChild(self.__class__.__name__)
        """:obj:`logging.Logger`: Logger for this object."""

        self._auth = auth
        """:obj:`AuthModel`: Authentication object."""

        auth.check_login()

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return "{c.__module__}.{c.__name__}(auth={auth!r}, url={url!r})".format(
            c=self.__class__,
            auth=self._auth.__class__.__name__,
            url=self._auth._http_client.url,
        )

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    def _request(
        self, path, method="get", raw=False, is_json=True, check_status=True, **kwargs
    ):
        """Perform a REST API request.

        Args:
            path (:obj:`str`):
                Path to use in request.
            method (:obj:`str`, optional):
                HTTP method to use in request.

                Defaults to: "get".
            raw (:obj:`bool`, optional):
                Return the raw response. If False, return response text or json.

                Defaults to: False.
            is_json (:obj:`bool`, optional):
                Response should have JSON data.

                Defaults to: True.
            check_status (:obj:`bool`, optional):
                Call :meth:`_check_response_status`.

                Defaults to: True.
            **kwargs:
                Passed to :meth:`axonius_api_client.http.interfaces.HttpClient.__call__`

        Returns:
            :obj:`object` if is_json, or :obj:`str` if not is_json, or
            :obj:`requests.Response` if raw

        """
        sargs = {}
        sargs.update(kwargs)
        sargs.update({"path": path, "method": method})

        response = self._auth.http_client(**sargs)

        if check_status:
            self._check_response_status(response=response)

        if raw:
            return response

        if is_json:
            return self._check_response_json(response=response)

        return response.text

    def _check_response_status(self, response):
        """Check response status code.

        Raises:
            :exc:`exceptions.ResponseError`

        """
        if response.status_code != 200:
            raise exceptions.ResponseError(
                response=response, exc=None, details=True, bodies=True
            )

    def _check_response_json(self, response):
        """Check response is JSON.

        Raises:
            :exc:`exceptions.InvalidJson`

        """
        try:
            return response.json()
        except Exception as exc:
            raise exceptions.InvalidJson(response=response, exc=exc)
        # FUTURE: check for "error" in JSON dict
        # Need a way to reproduce response with "error" in JSON dict


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
