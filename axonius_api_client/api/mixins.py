# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import six
import abc

from .. import constants, exceptions, tools


@six.add_metaclass(abc.ABCMeta)
class Model(object):
    """API client for Axonius REST API."""

    @abc.abstractproperty
    def _router(self):
        """Router for this API client.

        Returns:
            :obj:`axonius_api_client.api.routers.Router`

        """
        raise NotImplementedError  # pragma: no cover


@six.add_metaclass(abc.ABCMeta)
class ModelUserDevice(Model):
    """API client for Axonius REST API."""

    @abc.abstractproperty
    def _default_fields(self):
        """Fields to set as default for methods with fields as kwargs.

        Returns:
            :obj:`dict`

        """
        raise NotImplementedError  # pragma: no cover


class Mixins(Model):
    """API client for Axonius REST API."""

    def __init__(self, auth, **kwargs):
        """Constructor.

        Args:
            auth (:obj:`AuthModel`):
                Authentication object.

        """
        log_level = kwargs.get("log_level", constants.LOG_LEVEL_API)
        self._log = tools.logs.get_obj_log(obj=self, level=log_level)
        """:obj:`logging.Logger`: Logger for this object."""

        self._auth = auth
        """:obj:`AuthModel`: Authentication object."""

        self._init(auth=auth, **kwargs)

        auth.check_login()

    def _init(self, auth, **kwargs):
        """Pass."""
        pass

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return "{c.__module__}.{c.__name__}(auth={auth!r}, url={url!r})".format(
            c=self.__class__,
            auth=self._auth.__class__.__name__,
            url=self._auth._http.url,
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
                Passed to :meth:`axonius_api_client.http.client.HttpClient.__call__`

        Returns:
            :obj:`object` if is_json, or :obj:`str` if not is_json, or
            :obj:`requests.Response` if raw

        """
        sargs = {}
        sargs.update(kwargs)
        sargs.update({"path": path, "method": method})

        response = self._auth.http(**sargs)

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
        # TODO: check for "error" in JSON dict
        # Need a way to reproduce response with "error" in JSON dict

    def _check_max_page_size(self, page_size):
        """Check if page size is over :data:`axonius_api_client.constants.MAX_PAGE_SIZE`.

        Args:
            page_size (:obj:`int`):
                Page size to check.

        Raises:
            :exc:`exceptions.ApiError`

        """
        if page_size > constants.MAX_PAGE_SIZE:
            msg = "Page size {page_size} is over maximum page size {max_size}"
            msg = msg.format(page_size=page_size, max_size=constants.MAX_PAGE_SIZE)
            raise exceptions.ApiError(msg)


class Child(object):
    """Pass."""

    def __init__(self, parent):
        """Pass."""
        self._parent = parent
        self._log = parent._log.getChild(self.__class__.__name__)

    def __str__(self):
        """Pass."""
        return "{} for {}".format(self.__class__.__name__, self._parent)

    def __repr__(self):
        """Pass."""
        return self.__str__()


class Parser(object):
    """Pass."""

    def __init__(self, raw, parent):
        """Pass."""
        self._parent = parent
        self._raw = raw

    def __str__(self):
        """Pass."""
        return "{} for {}".format(self.__class__.__name__, self._parent)

    def __repr__(self):
        """Pass."""
        return self.__str__()
