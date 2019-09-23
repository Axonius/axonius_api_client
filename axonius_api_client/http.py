# -*- coding: utf-8 -*-
"""Axonius API HTTP client module."""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import warnings

import requests
import six

from . import constants, exceptions, logs, tools, version

InsecureRequestWarning = requests.urllib3.exceptions.InsecureRequestWarning


class Http(object):
    """HTTP client for sending requests usings :obj:`requests.Session`.

    Attributes:
        session (:obj:`requests.Session`): Session object for sending requests.
        url (:obj:`str`): URL of Axonius instance.

    """

    def __init__(
        self,
        url,
        connect_timeout=5,
        response_timeout=60,
        certpath=None,
        certwarn=True,
        certverify=False,
        http_proxy=None,
        https_proxy=None,
        save_last=True,
        save_history=False,
        # fmt: off
        **kwargs
        # fmt: on
    ):
        """Constructor.

        Args:
            url (:obj:`str` or :obj:`axonius_api_client.http.parser.ParserUrl`):
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

                Defaults to: None.
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
            http_proxy (:obj:`str`, optional):
                HTTP proxy to use when connecting to url.

                Defaults to: None.
            https_proxy (:obj:`str`, optional):
                HTTPS proxy to use when connecting to url.

                Defaults to: None.
            save_last (:obj:`bool`, optional):
                Save last request & response to :attr:`_LAST_REQUEST` and
                :attr:`_LAST_RESPONSE`.

                Defaults to: True.
            save_history (:obj:`bool`, optional):
                Add last response to :attr:`_HISTORY`.

                Defaults to: False.
            kwargs:
                log_level (:obj:`str`):
                    Control logging level of object.

                    Defaults to: :attr:`constants.LOG_LEVEL_HTTP`.
                log_level_urllib (:obj:`str`):
                    Control logging level of urllib.

                    Defaults to: "warning".
                log_request_attrs (:obj:`bool`):
                    Control request attr logging.
                    True = verbose, False = brief, None = none

                    Defaults to: None.
                log_response_attrs (:obj:`bool`):
                    Control response attr logging.
                    True = verbose, False = brief, None = none

                    Defaults to: None.
                log_request_body (:obj:`bool`):
                    Control request body logging.

                    Defaults to: False.
                log_response_body (:obj:`bool`):
                    Control response body logging.

                    Defaults to: False.

        """
        log_level = kwargs.get("log_level", constants.LOG_LEVEL_HTTP)
        self._log = logs.get_obj_log(obj=self, level=log_level)
        """:obj:`logging.Logger`: Logger for this object."""

        if isinstance(url, ParserUrl):
            self._URLPARSED = url
        else:
            self._URLPARSED = ParserUrl(url=url, default_scheme="https")

        self.url = self._URLPARSED.url
        """:obj:`str`: URL of Axonius API."""

        self._LAST_REQUEST = None
        """:obj:`requests.PreparedRequest`: Last request sent."""

        self._LAST_RESPONSE = None
        """:obj:`requests.Response`: Last response received."""

        self._SAVE_LAST = save_last
        """:obj:`bool`: Save requests to last_request and responses to last_response."""

        self._HISTORY = []
        """:obj:`list` of :obj:`requests.Response`: History of responses."""

        self._SAVE_HISTORY = save_history
        """:obj:`bool`: Append all responses to history."""

        self._CONNECT_TIMEOUT = connect_timeout
        """:obj:`int`: Seconds to wait for connection to url to open."""

        self._RESPONSE_TIMEOUT = response_timeout
        """:obj:`int`: Seconds to wait for response from url."""

        self.session = requests.Session()
        """:obj:`requests.Session`: Session object to use."""

        self.session.verify = certpath if certpath else certverify
        self.session.proxies = {}
        self.session.proxies["https"] = https_proxy
        self.session.proxies["http"] = http_proxy

        self._LOG_REQUEST_BODY = kwargs.get("log_request_body", False)
        """:obj:`bool`: Log the full request body."""

        self._LOG_RESPONSE_BODY = kwargs.get("log_response_body", False)
        """:obj:`bool`: Log the full response body."""

        self._LOG_RESPONSE_ATTRS = []
        """:obj:`list` of :obj:`str`: Request attributes to log."""

        self._LOG_REQUEST_ATTRS = []
        """:obj:`list` of :obj:`str`: Response attributes to log."""

        log_response_attrs = kwargs.get("log_response_attrs", None)
        if log_response_attrs is True:
            self._LOG_RESPONSE_ATTRS = constants.LOG_RESPONSE_ATTRS_VERBOSE
        elif log_response_attrs is False:
            self._LOG_RESPONSE_ATTRS = constants.LOG_RESPONSE_ATTRS_BRIEF

        log_request_attrs = kwargs.get("log_request_attrs", None)
        if log_request_attrs is True:
            self._LOG_REQUEST_ATTRS = constants.LOG_REQUEST_ATTRS_VERBOSE
        elif log_request_attrs is False:
            self._LOG_REQUEST_ATTRS = constants.LOG_REQUEST_ATTRS_BRIEF

        if certwarn is True:
            warnings.simplefilter("once", InsecureRequestWarning)
        elif certwarn is False:
            warnings.simplefilter("ignore", InsecureRequestWarning)

        urllog = logging.getLogger("urllib3.connectionpool")
        logs.set_level(obj=urllog, level=kwargs.get("log_level_urllib", "warning"))

    def __call__(
        self,
        path=None,
        route=None,
        method="get",
        data=None,
        params=None,
        headers=None,
        json=None,
        files=None,
        # fmt: off
        **kwargs
        # fmt: on
    ):
        """Create, prepare, and then send a request using :attr:`session`.

        Args:
            path (:obj:`str`, optional):
                Path to append to :attr:`url` for this request.

                Defaults to: None.
            route (:obj:`str`, optional):
                Route to append to path for this request.

                Defaults to: None.
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
            json (:obj:`dict`, optional):
                Dictionary to encode as JSON string and send in request.

                Defaults to: None.
            files (:obj:`tuple` of :obj:`tuple`, optional):
                Files to attach to request.

                Defaults to: None.
            kwargs:
                connect_timeout (:obj:`int`): Override object connect timeout.
                response_timeout (:obj:`int`): Override object response timeout.
                proxies (:obj:`dict`): Override object proxies.
                verify (:obj:`bool` or :obj:`str`): Override object verify.
                stream (:obj:`object`): See requests docs.
                cert (:obj:`str`): See requests docs.

        Returns:
            :obj:`requests.Response`

        """
        url = tools.join_url(self.url, path, route)

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

        if self._SAVE_LAST:
            self._LAST_REQUEST = prepped_request

        if self._LOG_REQUEST_ATTRS:
            msg = ", ".join(self._LOG_REQUEST_ATTRS)
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
            kwargs.get("connect_timeout", self._CONNECT_TIMEOUT),
            kwargs.get("response_timeout", self._RESPONSE_TIMEOUT),
        )

        if self._LOG_REQUEST_BODY:
            msg = "request body:\n{body}"
            msg = msg.format(
                body=tools.json_dump(obj=prepped_request.body, error=False)
            )
            self._log.debug(msg)

        response = self.session.send(**send_args)

        if self._SAVE_LAST:
            self._LAST_RESPONSE = response

        if self._SAVE_HISTORY:
            self._HISTORY.append(response)

        if self._LOG_RESPONSE_ATTRS:
            msg = ", ".join(self._LOG_RESPONSE_ATTRS)
            msg = msg.format(response=response, size=len(response.text or ""))
            self._log.debug(msg)

        if self._LOG_RESPONSE_BODY:
            msg = "response body:\n{body}"
            msg = msg.format(body=tools.json_dump(obj=response.text, error=False))
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


class ParserUrl(object):
    """Parse a URL and ensure it has the neccessary bits."""

    def __init__(self, url, default_scheme="https"):
        """Constructor.

        Args:
            url (:obj:`str`):
                URL to parse
            default_scheme (:obj:`str`, optional):
                If no scheme in URL, use this.

                Defaults to: "https"

        Raises:
            :exc:`exceptions.HttpError`:
                If parsed URL winds up without a hostname, port, or scheme.

        """
        self._init_url = url
        """:obj:`str`: Initial URL provided."""

        self._init_scheme = default_scheme
        """:obj:`str`: Default scheme provided."""

        self._init_parsed = six.moves.urllib.parse.urlparse(url)
        """:obj:`urllib.parse.ParseResult`: First pass of parsing URL."""

        self.parsed = self.reparse(
            parsed=self._init_parsed, default_scheme=default_scheme
        )
        """:obj:`urllib.parse.ParseResult`: Second pass of parsing URL."""

        for part in ["hostname", "port", "scheme"]:
            if not getattr(self.parsed, part, None):
                error = (
                    "Parsed URL into {pstr!r} and no {part!r} provided in URL {url!r}"
                )
                error = error.format(part=part, url=url, pstr=self.parsed_str)
                raise exceptions.HttpError(error)

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        msg = "{c.__module__}.{c.__name__}({parsed})".format
        return msg(c=self.__class__, parsed=self.parsed_str)

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    @property
    def hostname(self):
        """Hostname part from :attr:`ParserUrl.parsed`.

        Returns:
            :obj:`str`

        """
        return self.parsed.hostname

    @property
    def port(self):
        """Port part from :attr:`ParserUrl.parsed`.

        Returns
            :obj:`int`

        """
        return int(self.parsed.port)

    @property
    def scheme(self):
        """Scheme part from :attr:`ParserUrl.parsed`.

        Returns:
            :obj:`str`

        """
        return self.parsed.scheme

    @property
    def url(self):
        """Get scheme, hostname, and port from :attr:`ParserUrl.parsed`.

        Returns:
            :obj:`str`

        """
        return self.unparse_base(parsed_result=self.parsed)

    @property
    def url_full(self):
        """Get full URL from :attr:`ParserUrl.parsed`.

        Returns:
            :obj:`str`

        """
        return self.unparse_all(parsed_result=self.parsed)

    @property
    def parsed_str(self):
        """Create string of :attr:`ParserUrl.parsed`.

        Returns:
            :obj:`str`

        """
        parsed = getattr(self, "parsed", None)
        attrs = [
            "scheme",
            "netloc",
            "hostname",
            "port",
            "path",
            "params",
            "query",
            "fragment",
        ]
        atmpl = "{a}={v!r}".format
        attrs = [atmpl(a=a, v="{}".format(getattr(parsed, a, "")) or "") for a in attrs]
        return ", ".join(attrs)

    def make_netloc(self, host, port):
        """Create netloc from host and port.

        Args:
            host (:obj:`str`):
                Host part to use in netloc.
            port (:obj:`str`):
                Port part to use in netloc.

        Returns:
            :obj:`str`

        """
        return ":".join([host, port]) if port else host

    def reparse(self, parsed, default_scheme=""):
        """Reparse a parsed URL into a parsed URL with values fixed.

        Args:
            parsed (:obj:`urllib.parse.ParseResult`):
                Parsed URL to reparse.
            default_scheme (:obj:`str`, optional):
                If no scheme in URL, use this.

                Defaults to: ""

        Returns:
            :obj:`urllib.parse.ParseResult`

        """
        scheme, netloc, path, params, query, fragment = parsed
        host = parsed.hostname
        port = format(parsed.port or "")

        if not netloc and scheme and path and path.split("/")[0].isdigit():
            """For case:
            >>> urllib.parse.urlparse('host:443/')
            ParseResult(
                scheme='host', netloc='', path='443/', params='', query='', fragment=''
            )
            """
            host = scheme  # switch host from scheme to host
            port = path.split("/")[0]  # remove / from path and assign to port
            path = ""  # empty out path
            scheme = default_scheme
            netloc = ":".join([host, port])

        if not netloc and path:
            """For cases:
            >>> urllib.parse.urlparse('host:443')
            ParseResult(
                scheme='', netloc='', path='host:443', params='', query='', fragment=''
            )
            >>> urllib.parse.urlparse('host')
            ParseResult(
                scheme='', netloc='', path='host', params='', query='', fragment=''
            )
            """
            netloc, path = path, netloc
            if ":" in netloc:
                host, port = netloc.split(":", 1)
                netloc = ":".join([host, port]) if port else host
            else:
                host = netloc

        scheme = scheme or default_scheme
        if not scheme and port:
            if format(port) == "443":
                scheme = "https"
            elif format(port) == "80":
                scheme = "http"

        if not port:
            if scheme == "https":
                netloc = self.make_netloc(host, "443")
            elif scheme == "http":
                netloc = self.make_netloc(host, "80")

        pass2 = six.moves.urllib.parse.urlunparse(
            (scheme, netloc, path, params, query, fragment)
        )
        return six.moves.urllib.parse.urlparse(pass2)

    def unparse_base(self, parsed_result):
        """Unparse a parsed URL into just the scheme, hostname, and port parts.

        Args:
            parsed_result (:obj:`urllib.parse.ParseResult`):
                Parsed URL to unparse.

        Returns:
            :obj:`str`

        """
        # only unparse self.parsed into url with scheme and netloc
        bits = (parsed_result.scheme, parsed_result.netloc, "", "", "", "")
        return six.moves.urllib.parse.urlunparse(bits)

    def unparse_all(self, parsed_result):
        """Unparse a parsed URL with all the parts.

        Args:
            parsed_result (:obj:`urllib.parse.ParseResult`):
                Parsed URL to unparse.

        Returns:
            :obj:`str`

        """
        return six.moves.urllib.parse.urlunparse(parsed_result)
