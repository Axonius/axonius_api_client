# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import abc

import six

from .. import constants, exceptions, logs


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

    def __init__(self, auth, **kwargs):
        """Client for Axonius REST API.

        Args:
            auth (:obj:`AuthModel`):
                Authentication object.

        """
        log_level = kwargs.get("log_level", constants.LOG_LEVEL_API)
        self._log = logs.get_obj_log(obj=self, level=log_level)
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
        error_json_bad_status=True,
        error_json_invalid=True,
        # fmt: off
        **kwargs
        # fmt: on
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
                Call :meth:`_check_response_code`.

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

        if raw:
            return response

        if is_json and response.text:
            data = self._check_response_json(
                response=response,
                error_json_bad_status=error_json_bad_status,
                error_json_invalid=error_json_invalid,
            )
        else:
            data = response.text

        self._check_response_code(response=response, error_status=error_status)

        return data

    def _check_response_code(self, response, error_status=True):
        """Check response status code.

        Raises:
            :exc:`exceptions.ResponseError`

        """
        if error_status:
            try:
                response.raise_for_status()
            except Exception as exc:
                raise exceptions.ResponseNotOk(
                    response=response, exc=exc, details=True, bodies=True
                )

    def _check_response_json(
        self, response, error_json_bad_status=True, error_json_invalid=True
    ):
        """Check response is JSON.

        Raises:
            :exc:`exceptions.InvalidJson`

        """
        try:
            data = response.json()
        except Exception as exc:
            if error_json_invalid:
                raise exceptions.JsonInvalid(response=response, exc=exc)
            return response.text

        if isinstance(data, dict):
            has_error = data.get("error")
            has_error_status = data.get("status") == "error"

            if (has_error or has_error_status) and error_json_bad_status:
                raise exceptions.JsonError(response=response, data=data)

        return data


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
        self._log = parent._log.getChild(self.__class__.__name__)

    @abc.abstractmethod
    def parse(self):
        """Pass."""
        raise NotImplementedError  # pragma: no cover
