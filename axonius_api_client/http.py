# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import warnings
import logging

import requests

from . import exceptions
from . import version

LOG = logging.getLogger(__name__)


class HttpClient(object):
    """Wrapper for sending requests usings :obj:`requests.Session`."""

    _LOG_REQUEST_ATTRS = [
        "request to {request.url!r}",
        "method={request.method!r}",
        "headers={request.headers}",
        "size={size}",
    ]
    """:obj:`list` of :obj:`str`: attributes to include when logging requests."""

    _LOG_RESPONSE_ATTRS = [
        "response from {response.url!r}",
        "method={response.request.method!r}",
        "status={response.status_code!r}",
        "reason={response.reason!r}",
        "elapsed={response.elapsed}",
        "size={size}",
    ]
    """:obj:`list` of :obj:`str`: attributes to include when logging responses."""

    def __init__(self, url, connect_timeout=5, response_timeout=5, verify=False):
        """Constructor.

        Args:
            url (:obj:`str`):
                Axonius API URL.
            connect_timeout (:obj:`int`, optional):
                Seconds to wait for connection to url to open.

                Defaults to: 5.
            response_timeout (:obj:`int`, optional):
                Seconds to wait for response from url.

                Defaults to: 5.
            verify (:obj:`bool` or :obj:`str`, optional):
                Enable/Disable SSL cert validation.

                Defaults to: False.

        Notes:
            If verify is False, no SSL cert verification is done.

            If verify is True, SSL cert verification is done using the default CA bundle
            for this OS.

            If verify is str, SSL cert verification is done using CA bundle at path.

            If :attr:`requests.Session.trust_env` is False or verify is False,
            no OS environment variables are used at all.

            If :attr:`requests.Session.trust_env` is True and verify is True, OS env
            variables $REQUESTS_CA_BUNDLE, and $CURL_CA_BUNDLE are used for path to
            CA bundle if set.

            Caveat: If previous request was made with :attr:`session` and
            :attr:`requests.Session.verify` is changed but
            :meth:`requests.Session.close` has not been called, the new verify will
            not be used.

        """

        self._log = LOG.getChild(self.__class__.__name__)
        """:obj:`logging.Logger`: Logger for this object."""

        self._url = url
        """:obj:`str`: URL of Axonius API."""

        self._last_request = None
        """:obj:`requests.PreparedRequest`: Last request sent."""

        self._last_response = None
        """:obj:`requests.Response`: Last response received."""

        self._save_last = False
        """:obj:`bool`: Save requests to last_request and responses to last_response."""

        self._history = []
        """:obj:`list` of :obj:`requests.Response`: History of responses."""

        self._save_history = False
        """:obj:`bool`: Append all responses to history."""

        self._connect_timeout = connect_timeout
        """:obj:`int`: Seconds to wait for connection to url to open."""

        self._response_timeout = response_timeout
        """:obj:`int`: Seconds to wait for response from url."""

        self._session = requests.Session()
        """:obj:`requests.Session`: Session object to use."""

        self._session.verify = verify

        if verify is False:
            warnings.simplefilter(
                "ignore", requests.urllib3.exceptions.InsecureRequestWarning
            )

    def __call__(
        self,
        path,
        route="",
        method="get",
        data=None,
        params=None,
        headers=None,
        json=None,
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
        url = requests.compat.urljoin(self._url, path)
        if route:
            url = requests.compat.urljoin(url, route.lstrip("/"))

        headers = headers or {}
        headers.setdefault("User-Agent", self._user_agent)

        request = requests.Request(
            url=url, method=method, data=data, headers=headers, params=params, json=json
        )
        prepped_request = self._session.prepare_request(request=request)

        if self._save_last:
            self._last_request = prepped_request

        if self._LOG_REQUEST_ATTRS:
            msg = ", ".join(self._LOG_REQUEST_ATTRS)
            msg = msg.format(
                request=prepped_request, size=len(prepped_request.body or "")
            )
            self._log.debug(msg)

        psettings = self._session.merge_environment_settings(
            url=prepped_request.url,
            proxies=kwargs.get("proxies", None),
            stream=kwargs.get("stream", None),
            verify=kwargs.get("verify", None),
            cert=kwargs.get("cert", None),
        )

        send_args = {}
        send_args.update(psettings)
        send_args["request"] = prepped_request
        send_args["timeout"] = (
            kwargs.get("connect_timeout", self._connect_timeout),
            kwargs.get("response_timeout", self._response_timeout),
        )

        response = self._session.send(**send_args)

        if self._save_last:
            self._last_response = response

        if self._save_history:
            self._history.append(response)

        if self._LOG_RESPONSE_ATTRS:
            msg = ", ".join(self._LOG_RESPONSE_ATTRS)
            msg = msg.format(response=response, size=len(response.text or ""))
            self._log.debug(msg)

        return response

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        bits = ["url={!r}".format(self._url)]
        bits = "({})".format(", ".join(bits))
        cls = "{c.__module__}.{c.__name__}".format(c=self.__class__)
        return "{cls}{bits}".format(cls=cls, bits=bits)

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    @property
    def _user_agent(self):
        """Build a user agent string for use in User-Agent header.

        Returns:
            :obj:`str`

        """
        msg = "{name}.{clsname}/{ver}"
        return msg.format(
            name=__name__, clsname=self.__class__.__name__, ver=version.__version__
        )


class UrlParser(object):
    """Parse a URL and ensure it has the neccessary bits."""

    def __init__(self, url, default_scheme=""):
        """Constructor.

        Args:
            url (:obj:`str`):
                URL to parse
            default_scheme (:obj:`str`, optional):
                If no scheme in URL, use this.

                Defaults to: ""

        Raises:
            :exc:`exceptions.PackageError`:
                If parsed URL winds up without a hostname, port, or scheme.

        """
        self._init_url = url
        """:obj:`str`: Initial URL provided."""
        self._init_scheme = default_scheme
        """:obj:`str`: Default scheme provided."""
        self._init_parsed = requests.compat.urlparse(url)
        """:obj:`urllib.parse.ParseResult`: First pass of parsing URL."""
        self.parsed = self.reparse(
            parsed=self._init_parsed, default_scheme=default_scheme
        )
        """:obj:`urllib.parse.ParseResult`: Second pass of parsing URL."""

        for part in ["hostname", "port", "scheme"]:
            if not getattr(self.parsed, part, None):
                error = "\n".join(
                    [
                        "",
                        "Parsed into: {pstr}",
                        "URL format should be like: scheme://hostname:port",
                        "No {part} provided in URL {url!r}",
                    ]
                )
                error = error.format(part=part, url=url, pstr=self.parsed_str)
                raise exceptions.PackageError(error)

    def __str__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        bits = ["parsed={!r}".format(self.parsed_str)]
        bits = "({})".format(", ".join(bits))
        cls = "{c.__module__}.{c.__name__}".format(c=self.__class__)
        return "{cls}{bits}".format(cls=cls, bits=bits)

    def __repr__(self):
        """Show object info.

        Returns:
            :obj:`str`

        """
        return self.__str__()

    @property
    def hostname(self):
        """Hostname part from :attr:`UrlParser.parsed`.

        Returns:
            :obj:`str`

        """
        return self.parsed.hostname

    @property
    def port(self):
        """Port part from :attr:`UrlParser.parsed`.

        Returns:
            :obj:`int`

        """
        return int(self.parsed.port)

    @property
    def scheme(self):
        """Scheme part from :attr:`UrlParser.parsed`.

        Returns:
            :obj:`str`

        """
        return self.parsed.scheme

    @property
    def url(self):
        """Get scheme, hostname, and port from :attr:`UrlParser.parsed`.

        Returns:
            :obj:`str`

        """
        return self.unparse_base(p=self.parsed)

    @property
    def url_full(self):
        """Get full URL from :attr:`UrlParser.parsed`.

        Returns:
            :obj:`str`

        """
        return self.unparse_all(p=self.parsed)

    @property
    def parsed_str(self):
        """Create string of :attr:`UrlParser.parsed`.

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
        vals = ", ".join(
            [
                "{a}={v!r}".format(a=a, v="{}".format(getattr(parsed, a, "")) or "")
                for a in attrs
            ]
        )
        return vals

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
        netloc = ":".join([host, port]) if port else host
        return netloc

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
                port = "443"
                netloc = self.make_netloc(host, port)
            elif scheme == "http":
                port = "80"
                netloc = self.make_netloc(host, port)

        pass2 = requests.compat.urlunparse(
            (scheme, netloc, path, params, query, fragment)
        )
        ret = requests.compat.urlparse(pass2)
        return ret

    def unparse_base(self, p):
        """Unparse a parsed URL into just the scheme, hostname, and port parts.

        Args:
            p (:obj:`urllib.parse.ParseResult`):
                Parsed URL to unparse.

        Returns:
            :obj:`str`

        """
        # only unparse self.parsed into url with scheme and netloc
        return requests.compat.urlunparse((p.scheme, p.netloc, "", "", "", ""))

    def unparse_all(self, p):
        """Unparse a parsed URL with all the parts.

        Args:
            p (:obj:`urllib.parse.ParseResult`):
                Parsed URL to unparse.

        Returns:
            :obj:`str`

        """
        return requests.compat.urlunparse(p)
