# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import abc

import six

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


class Mixins(object):
    """API client for Axonius REST API."""

    _LIMIT_CHECKS = ["json", "params"]
    _LIMIT_KEYS = ["limit"]

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
        self,
        path,
        method="get",
        raw=False,
        is_json=True,
        error_status=True,
        error_json=True,
        **kwargs
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
            error_status (:obj:`bool`, optional):
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

        for limit_check in self._LIMIT_CHECKS:
            for limit_key in self._LIMIT_KEYS:
                if limit_key in kwargs.get(limit_check, {}):
                    self._check_max_page_size(kwargs[limit_check][limit_key])

        response = self._auth.http(**sargs)

        if raw:
            return response

        if is_json and response.text:
            data = self._check_response_json(response=response, error_json=error_json)
        else:
            data = response.text

        if error_status:
            self._check_response_status(response=response)

        return data

    def _check_response_status(self, response):
        """Check response status code.

        Raises:
            :exc:`exceptions.ResponseError`

        """
        if response.status_code != 200:
            raise exceptions.ResponseError(
                response=response, exc=None, details=True, bodies=True
            )

    def _check_response_json(self, response, error_json=True):
        """Check response is JSON.

        Raises:
            :exc:`exceptions.InvalidJson`

        """
        try:
            data = response.json()
        except Exception as exc:
            if error_json:
                raise exceptions.JsonInvalid(response=response, exc=exc)

        if tools.is_type.dict(data):
            has_error = data.get("error")
            has_error_status = data.get("status") == "error"

            if (has_error or has_error_status) and error_json:
                raise exceptions.JsonError(response=response, data=data)

        return data

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

    def _check_counts(
        self,
        value,
        value_type,
        objtype,
        count_total,
        count_min,
        count_max,
        error=True,
        known=None,
    ):
        """Pass."""
        if count_min == 1 and count_max == 1:
            if count_total != 1 and error:
                raise exceptions.ObjectNotFound(
                    value=value,
                    value_type=value_type,
                    object_type=objtype,
                    known=known,
                    count_total=count_total,
                )
            return True

        if count_min is not None and count_total < count_min:
            if error:
                raise exceptions.TooFewObjectsFound(
                    value=value,
                    value_type=value_type,
                    object_type=objtype,
                    count_total=count_total,
                    count_min=count_min,
                )
            return True

        if count_max is not None and count_total > count_max:
            if error:
                raise exceptions.TooManyObjectsFound(
                    value=value,
                    value_type=value_type,
                    object_type=objtype,
                    count_total=count_total,
                    count_max=count_max,
                )
            return True
        return False

    def _only1(self, rows, count_max=None, count_min=None):
        """Pass."""
        if count_max is not None:
            if count_max == 1 and rows:
                return rows[0]
            elif rows:
                return rows[:count_max]
        return rows


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


@six.add_metaclass(abc.ABCMeta)
class Parser(Child):
    """Pass."""

    def __init__(self, raw, parent, **kwargs):
        """Pass."""
        self._parent = parent
        self._raw = raw

    @abc.abstractmethod
    def parse(self):
        """Pass."""
        raise NotImplementedError  # pragma: no cover
