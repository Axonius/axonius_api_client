# -*- coding: utf-8 -*-
"""API model base classes and mixins."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import abc

from .. import constants, exceptions, logs


class Model(object):
    """API model base class."""

    @abc.abstractproperty
    def _router(self):
        """Router for this API model.

        Returns:
            :obj:`.routers.Router`: REST API route defs
        """
        raise NotImplementedError  # pragma: no cover


class ModelAsset(Model):
    """API model base class for asset types."""

    @abc.abstractproperty
    def _default_fields(self):
        """Fields to add to all get calls for this asset type.

        Returns:
            :obj:`list` of :obj:`dict`: fields to add to
        """
        raise NotImplementedError  # pragma: no cover


class Mixins(object):
    """Mixins for :obj:`Model` objects."""

    def __init__(self, auth, **kwargs):
        """Mixins for :obj:`Model` objects.

        Args:
            auth (:obj:`.auth.Model`): object to use for auth and sending API requests
            **kwargs: passed to :meth:`Mixins._init`
        """
        log_level = kwargs.get("log_level", constants.LOG_LEVEL_API)
        self._log = logs.get_obj_log(obj=self, level=log_level)
        """:obj:`logging.Logger`: Logger for this object."""

        self._auth = auth
        """:obj:`.auth.Model`: object to use for auth and sending API requests."""

        self._init(auth=auth, **kwargs)

        auth.check_login()

    def _init(self, auth, **kwargs):
        """Post init method for subclasses to use for extra setup.

        Args:
            auth (:obj:`.auth.Model`): object to use for auth and sending API requests
        """
        pass

    def __str__(self):
        """Show info for this model object."""
        return "{c.__module__}.{c.__name__}(auth={auth!r}, url={url!r})".format(
            c=self.__class__,
            auth=self._auth.__class__.__name__,
            url=self._auth._http.url,
        )

    def __repr__(self):
        """Show info for this model object."""
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
        """Send a REST API request using :attr:`.auth.Mixins.http`.

        Args:
            path (:obj:`str`): path to use in request
            method (:obj:`str`, optional): default ``get`` - method to use in request
            raw (:obj:`bool`, optional): default ``False`` -

                * if ``True`` return the raw :obj:`requests.Response` object
                * if ``False`` return the text or json of the response based on is_json
            is_json (:obj:`bool`, optional): default ``True`` - if raw is False:

                * if ``True`` return the decoded json of the response text body
                * if ``False`` return the text body of the response
            error_status (:obj:`bool`, optional): default ``True`` -

                * if ``True`` check response status code
                  with :meth:`_check_response_code`
                * if ``False`` do not check response status code
            **kwargs:
                Passed to :meth:`.http.Http.__call__`

        Returns:
            :obj:`requests.Response` or :obj:`object` or :obj:`str`:

                * :obj:`requests.Response`: if raw is True
                * :obj:`object`: if raw is False and is_json is True
                * :obj:`str`: if raw is False and is_json is False
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
        """Check the status code of a response.

        Args:
            response (:obj:`requests.Response`): response object to check
            error_status (:obj:`bool`, optional): default ``True`` -

                * if ``True`` throw exc if response status code is bad
                * if ``False`` silently ignore bad response status codes

        Raises:
            :exc:`.exceptions.ResponseNotOk`:
                if response has a status code that is an error and error_status is True
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
        """Check the text body of a response is JSON.

        Args:
            response (:obj:`requests.Response`): response object to check
            error_json_bad_status (:obj:`bool`, optional): default ``True`` -

                * if ``True`` throw an exc if response is a json dict that
                  has a non-empty error key or a status key that == error
                * if ``False`` ignore error and status keys in response json dicts
            error_json_invalid (:obj:`bool`, optional): default ``True`` -

                * if ``True`` throw an exc if response is invalid json
                * if ``False`` return the text of response if response is invalid json

        Raises:
            :exc:`.exceptions.JsonInvalid`: if error_json_invalid is True and
                response has invalid json

            :exc:`.exceptions.JsonError`: if error_json_bad_status is True and
                response is a json dict that has a non-empty error key or a
                status key that == error

        Returns:
            :obj:`object` or :obj:`str`:

                * :obj:`object` if response has json data
                * :obj:`str` if response has invalid json data
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
    """Mixins model for children of :obj:`Model`."""

    def __init__(self, parent):
        """Mixins model for children of :obj:`Model`.

        Args:
            parent (:obj:`Model`): parent API model of this child
        """
        self._parent = parent
        self._log = parent._log.getChild(self.__class__.__name__)
        self._init(parent=parent)

    def _init(self, parent):
        """Post init method for subclasses to use for extra setup.

        Args:
            parent (:obj:`Model`): parent API model of this child
        """
        pass

    def _request(self, **kwargs):
        """Get the response of parents :obj:`Mixins._request`.

        Args:
            **kwargs: passed to :obj:`Mixins._request`

        Returns:
            :obj:`object`: response from :obj:`Mixins._request`
        """
        return self._parent._request(**kwargs)

    @property
    def _router(self):
        """Get the parents :attr:`Model._router`.

        Returns:
            :obj:`.routers.Router`: parents REST API route defs
        """
        return self._parent._router

    def __str__(self):
        """Show info for this model object."""
        return "{} for {}".format(self.__class__.__name__, self._parent)

    def __repr__(self):
        """Show info for this model object."""
        return self.__str__()


class Parser(object):
    """Parser base class."""

    def __init__(self, raw, parent, **kwargs):
        """Parser base class.

        Args:
            raw (:obj:`object`): raw unparsed object
            parent (:obj:`Model` or :obj:`Child`):
                parent that called this parser
        """
        self._parent = parent
        self._raw = raw
        self._log = parent._log.getChild(self.__class__.__name__)
        self._init(parent=parent)

    def _init(self, parent):
        """Post init method for subclasses to use for extra setup.

        Args:
            parent (:obj:`Model` or :obj:`Child`):
                parent that called this parser
        """
        pass

    @abc.abstractmethod
    def parse(self):
        """Get the parsed object supplied to init."""
        raise NotImplementedError  # pragma: no cover

    def __str__(self):
        """Show info for this parser object."""
        return "{} for {}".format(self.__class__.__name__, self._parent)

    def __repr__(self):
        """Show info for this parser object."""
        return self.__str__()
