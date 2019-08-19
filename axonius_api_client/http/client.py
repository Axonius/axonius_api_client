# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import warnings
import logging

import requests

from . import parser
from .. import constants, tools, version, logs


class HttpClient(object):
    """Wrapper for sending requests usings :obj:`requests.Session`."""

    def __init__(
        self,
        url,
        connect_timeout=5,
        response_timeout=60,
        certpath="",
        certwarn=True,
        certverify=False,
        http_proxy="",
        https_proxy="",
        save_last=True,
        save_history=False,
        **kwargs
    ):
        """Constructor.

        Args:
            url (:obj:`str` or :obj:`axonius_api_client.http.parser.UrlParser`):
                Axonius API URL.
            connect_timeout (:obj:`int`, optional):
                Seconds to wait for connection to url to open.

                Defaults to: 5.
            response_timeout (:obj:`int`, optional):
                Seconds to wait for response from url.

                Defaults to: 60.
            certpath (:obj:`str`, optional):
                Enable validation using a path to CA bundle instead of the system CA
                bundle.

                Defaults to: "".
            certwarn (:obj:`bool`, optional):
                Show InsecureRequestWarning.
                * True = Show warning just once.
                * False = Never show warning.
                * None = Show warning always.

                Defaults to: True.
            certverify (:obj:`bool`, optional):
                If certpath is empty, control SSL certification validation.
                * True = Throw errors if SSL certificate is invalid.
                * False = Throw warnings if SSL certificate is invalid.

                Defaults to: False.
            save_last (:obj:`bool`, optional):
                Save last request & response to :attr:`last_request` and
                :attr:`last_response`.

                Defaults to: True.
            save_history (:obj:`bool`, optional):
                Add last response to :attr:`history`.

                Defaults to: False.

        """
        log_level = kwargs.get("log_level", constants.LOG_LEVEL_HTTP)
        self._log = logs.get_obj_log(obj=self, level=log_level)
        """:obj:`logging.Logger`: Logger for this object."""

        if isinstance(url, parser.UrlParser):
            url = url.url
        else:
            parsed_url = parser.UrlParser(url=url, default_scheme="https")
            url = parsed_url.url

        self.url = url
        """:obj:`str`: URL of Axonius API."""

        self.last_request = None
        """:obj:`requests.PreparedRequest`: Last request sent."""

        self.last_response = None
        """:obj:`requests.Response`: Last response received."""

        self.save_last = save_last
        """:obj:`bool`: Save requests to last_request and responses to last_response."""

        self.history = []
        """:obj:`list` of :obj:`requests.Response`: History of responses."""

        self.save_history = save_history
        """:obj:`bool`: Append all responses to history."""

        self.connect_timeout = connect_timeout
        """:obj:`int`: Seconds to wait for connection to url to open."""

        self.response_timeout = response_timeout
        """:obj:`int`: Seconds to wait for response from url."""

        self.session = requests.Session()
        """:obj:`requests.Session`: Session object to use."""

        if certpath:
            self.session.verify = certpath
        else:
            self.session.verify = certverify

        self.session.proxies = {}

        if https_proxy:
            self.session.proxies["https"] = https_proxy

        if http_proxy:
            self.session.proxies["http"] = http_proxy

        urlwarn = requests.urllib3.exceptions.InsecureRequestWarning

        if certwarn is True:
            warnings.simplefilter("once", urlwarn)
        elif certwarn is False:
            warnings.simplefilter("ignore", urlwarn)

        log_attrs_request = kwargs.get("log_attrs_request", False)
        if log_attrs_request:
            self.LOG_REQUEST_ATTRS = constants.LOG_REQUEST_ATTRS_VERBOSE
        elif log_attrs_request is False:
            self.LOG_REQUEST_ATTRS = constants.LOG_REQUEST_ATTRS_BRIEF
        elif log_attrs_request is None:
            self.LOG_REQUEST_ATTRS = []

        log_attrs_response = kwargs.get("log_attrs_response", False)
        if log_attrs_response:
            self.LOG_RESPONSE_ATTRS = constants.LOG_RESPONSE_ATTRS_VERBOSE
        elif log_attrs_response is False:
            self.LOG_RESPONSE_ATTRS = constants.LOG_RESPONSE_ATTRS_BRIEF
        elif log_attrs_response is None:
            self.LOG_RESPONSE_ATTRS = []

        urllog = logging.getLogger("urllib3.connectionpool")
        logs.set_level(obj=urllog, level=kwargs.get("log_level_urllib", "warning"))

    def __call__(
        self,
        path="",
        route="",
        method="get",
        data=None,
        params=None,
        headers=None,
        json=None,
        files=None,
        **kwargs
    ):
        """Create, prepare, and then send a request using :attr:`session`.

        Args:
            path (:obj:`str`, optional):
                Path to append to :attr:`url` for this request.
            method (:obj:`str`, optional):
                Method to use.

                Defaults to: "get".
            data (:obj:`str`, optional):
                Data to send in request body.

                Defaults to: None.
            params (:obj:`dict`, optional):
                Parameters to encode in URL.

                Defaults to: None.
            headers (:obj:`dict`, optional):
                Headers to send in request.

                Defaults to: None.

        Returns:
            :obj:`requests.Response`

        """
        # FUTURE: doc kwargs and files
        url = tools.urljoin(self.url, path, route)

        headers = headers or {}
        headers.setdefault("User-Agent", self.user_agent)

        request = requests.Request(
            url=url,
            method=method,
            data=data,
            headers=headers,
            params=params,
            json=json,
            files=files or [],
        )
        prepped_request = self.session.prepare_request(request=request)

        if self.save_last:
            self.last_request = prepped_request

        if self.LOG_REQUEST_ATTRS:
            msg = ", ".join(self.LOG_REQUEST_ATTRS)
            msg = msg.format(
                request=prepped_request, size=len(prepped_request.body or "")
            )
            self._log.debug(msg)

        send_args = self.session.merge_environment_settings(
            url=prepped_request.url,
            proxies=kwargs.get("proxies", None),
            stream=kwargs.get("stream", None),
            verify=kwargs.get("verify", None),
            cert=kwargs.get("cert", None),
        )

        send_args["request"] = prepped_request
        send_args["timeout"] = (
            kwargs.get("connect_timeout", self.connect_timeout),
            kwargs.get("response_timeout", self.response_timeout),
        )

        response = self.session.send(**send_args)

        if self.save_last:
            self.last_response = response

        if self.save_history:
            self.history.append(response)

        if self.LOG_RESPONSE_ATTRS:
            msg = ", ".join(self.LOG_RESPONSE_ATTRS)
            msg = msg.format(response=response, size=len(response.text or ""))
            self._log.debug(msg)

        return response

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return "{c.__module__}.{c.__name__}(url={url!r})".format(
            c=self.__class__, url=self.url
        )

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    @property
    def user_agent(self):
        """Build a user agent string for use in User-Agent header.

        Returns:
            :obj:`str`

        """
        msg = "{name}.{clsname}/{ver}"
        return msg.format(
            name=__name__, clsname=self.__class__.__name__, ver=version.__version__
        )
