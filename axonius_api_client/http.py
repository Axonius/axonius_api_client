# -*- coding: utf-8 -*-
"""HTTP client."""
import logging
import pathlib
import warnings
from typing import List, Optional, Union
from urllib.parse import ParseResult, urlparse, urlunparse

import requests

from .constants import (
    LOG_LEVEL_HTTP,
    MAX_BODY_LEN,
    REQUEST_ATTR_MAP,
    RESPONSE_ATTR_MAP,
    TIMEOUT_CONNECT,
    TIMEOUT_RESPONSE,
)
from .exceptions import HttpError
from .logs import get_obj_log, set_log_level
from .tools import join_url, json_reload, listify, path_read
from .version import __version__

InsecureRequestWarning = requests.urllib3.exceptions.InsecureRequestWarning


class Http:
    """HTTP client wrapper around :obj:`requests.Session`."""

    def __init__(
        self,
        url: str,
        connect_timeout: int = TIMEOUT_CONNECT,
        response_timeout: int = TIMEOUT_RESPONSE,
        certpath: Optional[Union[str, pathlib.Path]] = None,
        certwarn: bool = True,
        certverify: bool = False,
        cert_client_both: Optional[Union[str, pathlib.Path]] = None,
        cert_client_cert: Optional[Union[str, pathlib.Path]] = None,
        cert_client_key: Optional[Union[str, pathlib.Path]] = None,
        http_proxy: Optional[str] = None,
        https_proxy: Optional[str] = None,
        save_last: bool = True,
        save_history: bool = False,
        log_level: Union[int, str] = LOG_LEVEL_HTTP,
        log_level_urllib: str = "warning",
        log_request_attrs: Optional[List[str]] = None,
        log_response_attrs: Optional[List[str]] = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
    ):
        """HTTP client wrapper around :obj:`requests.Session`.

        Notes:
            * If certpath is supplied, certverify is ignored
            * private key supplied to cert_client_key or cert_client_both
              can **NOT** be password encrypted

        Args:
            url (:obj:`str` or :obj:`ParserUrl`): URL to connect to
            connect_timeout (:obj:`int`, optional):
                default :data:`TIMEOUT_CONNECT` - seconds to
                wait for connections to open to :attr:`url`
            response_timeout (:obj:`int`, optional):
                default :data:`TIMEOUT_RESPONSE` - seconds to
                wait for responses from :attr:`url`
            certpath (:obj:`str` or :obj:`pathlib.Path`, optional): default ``None`` -
                path to CA bundle file to use when verifing certs offered by :attr:`url`
                instead of the system CA bundle
            certwarn (:obj:`bool`, optional): default ``True`` - show warnings from
                requests about certs offered by :attr:`url` that are self signed:

                * if ``True`` show warning only the first time it happens
                * if ``False`` never show warning
                * if ``None`` show warning every time it happens
            certverify (:obj:`bool`, optional): default ``False`` - control
                validation of certs offered by :attr:`url`:

                * if ``True`` raise exception if cert is invalid/self-signed
                * if ``False`` only raise exception if cert is invalid
            cert_client_both (:obj:`str` or :obj:`pathlib.Path`, optional):
                default ``None`` - path to cert file containing both the private key and
                cert to offer to :attr:`url`
            cert_client_cert (:obj:`str` or :obj:`pathlib.Path`, optional):
                default ``None`` - path to cert file to offer to :attr:`url`
                (*must also supply cert_client_key*)
            cert_client_key (:obj:`str` or :obj:`pathlib.Path`, optional):
                default ``None`` - path to private key file for cert_client_cert to
                offer to :attr:`url` (*must also supply cert_client_cert*)
            http_proxy (:obj:`str`, optional): default ``None`` - proxy to use
                when making http requests to :attr:`url`
            https_proxy (:obj:`str`, optional): default ``None`` - proxy to use
                when making https requests to :attr:`url`
            save_last (:obj:`bool`, optional): default ``True`` -

                * if ``True`` save request to :attr:`LAST_REQUEST` and
                  response to :attr:`LAST_RESPONSE`
                * if ``False`` do not save request to :attr:`LAST_REQUEST` and
                  response to :attr:`LAST_RESPONSE`
            save_history (:obj:`bool`, optional): default ``True`` -

                * if ``True`` append responses to :attr:`HISTORY`
                * if ``False`` do not append responses to :attr:`HISTORY`
            log_level (:obj:`str`):
              default :data:`axonius_api_client.LOG_LEVEL_HTTP` -
              logging level to use for this objects logger
            log_level_urllib (:obj:`str`): default ``"warning"`` -
              logging level to use for this urllib logger
            log_request_attrs (:obj:`bool`): default ``None`` - control logging
              of request attributes:

              * if ``True``, log request attributes defined in
                :data:`axonius_api_client.LOG_REQUEST_ATTRS_VERBOSE`
              * if ``False``, log request attributes defined in
                :data:`axonius_api_client.LOG_REQUEST_ATTRS_BRIEF`
              * if ``None``, do not log any request attributes
            log_response_attrs (:obj:`bool`): default ``None`` - control logging
              of response attributes:

              * if ``True``, log response attributes defined in
                :data:`axonius_api_client.LOG_RESPONSE_ATTRS_VERBOSE`
              * if ``False``, log response attributes defined in
                :data:`axonius_api_client.LOG_RESPONSE_ATTRS_BRIEF`
              * if ``None``, do not log any response attributes
            log_request_body (:obj:`bool`): default ``False`` - control logging
              of request bodies:

              * if ``True``, log request bodies
              * if ``False``, do not log request bodies
            log_response_body (:obj:`bool`): default ``False`` - control logging
              of response bodies:

              * if ``True``, log response bodies
              * if ``False``, do not log response bodies

        Raises:
            :exc:`HttpError`: if either cert_client_cert or cert_client_key
                are supplied, and the other is not supplied

            :exc:`HttpError`: if any of cert_path, cert_client_cert,
                cert_client_key, or cert_client_both are supplied and the file does
                not exist
        """
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        """:obj:`logging.Logger`: Logger for this object."""

        if isinstance(url, ParserUrl):
            self.URLPARSED: ParserUrl = url
        else:
            self.URLPARSED: ParserUrl = ParserUrl(url=url, default_scheme="https")

        self.url: str = self.URLPARSED.url
        """:obj:`str`: URL to connect to"""

        self.LAST_REQUEST: requests.PreparedRequest = None
        """:obj:`requests.PreparedRequest`: last request sent"""

        self.LAST_RESPONSE: requests.Response = None
        """:obj:`requests.Response`: last response received"""

        self.HISTORY: List[requests.Response] = []
        """:obj:`list` of :obj:`requests.Response`: all responses received."""

        self.SAVE_LAST: bool = save_last
        """:obj:`bool`: save requests to :attr:`LAST_REQUEST` and responses
        to :attr:`LAST_RESPONSE`"""

        self.SAVEHISTORY: bool = save_history
        """:obj:`bool`: Append all responses to :attr:`HISTORY`"""

        self.CONNECT_TIMEOUT: int = connect_timeout
        """:obj:`int`: seconds to wait for connections to open to :attr:`url`"""

        self.RESPONSE_TIMEOUT: int = response_timeout
        """:obj:`int`: seconds to wait for responses from :attr:`url`"""

        self.session: requests.Session = requests.Session()
        """:obj:`requests.Session`: session object to use"""

        self.LOG_HIDE_HEADERS: List[str] = ["api-key", "api-secret"]
        """Headers to hide when logging."""

        self.LOG_REQUEST_BODY: bool = log_request_body
        """:obj:`bool`: Log the full request body."""

        self.LOG_RESPONSE_BODY: bool = log_response_body
        """:obj:`bool`: Log the full response body."""

        self.log_request_attrs: Optional[List[str]] = log_request_attrs
        self.log_response_attrs: Optional[List[str]] = log_response_attrs

        self.session.proxies = {}
        self.session.proxies["https"] = https_proxy
        self.session.proxies["http"] = http_proxy

        if certpath:
            path_read(obj=certpath, binary=True)
            self.session.verify = certpath
        else:
            self.session.verify = certverify

        if cert_client_both:
            path_read(obj=cert_client_both, binary=True)
            self.session.cert = str(cert_client_both)
        elif cert_client_cert or cert_client_key:
            if not all([cert_client_cert, cert_client_key]):
                error = (
                    "You must supply both a 'cert_client_cert' and 'cert_client_key'"
                    " or use 'cert_client_both'!"
                )
                raise HttpError(error)

            path_read(obj=cert_client_cert, binary=True)
            path_read(obj=cert_client_key, binary=True)
            self.session.cert = (str(cert_client_cert), str(cert_client_key))

        if certwarn is True:
            warnings.simplefilter("once", InsecureRequestWarning)
        elif certwarn is False:
            warnings.simplefilter("ignore", InsecureRequestWarning)

        urllog = logging.getLogger("urllib3.connectionpool")
        set_log_level(obj=urllog, level=log_level_urllib)

    def __call__(
        self,
        path: Optional[str] = None,
        route: Optional[str] = None,
        method: str = "get",
        data: Optional[str] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        files: tuple = None,
        # fmt: off
        **kwargs
        # fmt: on
    ) -> requests.Response:
        """Create, prepare, and then send a request using :attr:`session`.

        Args:
            path (:obj:`str`, optional): default ``None`` - path to append to
                :attr:`url`
            route (:obj:`str`, optional): default ``None`` - route to append to
                :attr:`url`
            method (:obj:`str`, optional): default ``"get"`` - method to use
            data (:obj:`str`, optional): default ``None`` - body to send
            params (:obj:`dict`, optional): default ``None`` - parameters to url encode
            headers (:obj:`dict`, optional): default ``None`` - headers to send
            json (:obj:`dict`, optional): default ``None`` - obj to encode as json
            files (:obj:`tuple` of :obj:`tuple`, optional): default ``None`` - files to
                send
            **kwargs:
                overrides for object attributes

                * connect_timeout (:obj:`int`): default :attr:`CONNECT_TIMEOUT` -
                  seconds to wait for connection to open to :attr:`url`
                * response_timeout (:obj:`int`): default :attr:`RESPONSE_TIMEOUT` -
                  seconds to wait for for response from :attr:`url`
                * proxies (:obj:`dict`): default ``None`` -
                  use custom proxies instead of proxies defined in :attr:`session`
                * verify (:obj:`bool` or :obj:`str`): default ``None`` - use custom
                  verification of cert offered by :attr:`url` instead of verification
                  defined in :attr:`session`
                * cert (:obj:`str`): default ``None`` - use custom
                  client cert to offer to :attr:`url` cert defined in :attr:`session`

        Returns:
            :obj:`requests.Response`: raw response object

        """
        url = join_url(self.url, path, route)

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

        if self.SAVE_LAST:
            self.LAST_REQUEST = prepped_request

        self._do_log_request(request=prepped_request)

        send_args = self.session.merge_environment_settings(
            url=prepped_request.url,
            proxies=kwargs.get("proxies", {}),
            stream=kwargs.get("stream", None),
            verify=kwargs.get("verify", None),
            cert=kwargs.get("cert", None),
        )

        send_args["request"] = prepped_request
        send_args["timeout"] = (
            kwargs.get("connect_timeout", self.CONNECT_TIMEOUT),
            kwargs.get("response_timeout", self.RESPONSE_TIMEOUT),
        )

        response = self.session.send(**send_args)

        if self.SAVE_LAST:
            self.LAST_RESPONSE = response

        if self.SAVEHISTORY:
            self.HISTORY.append(response)

        self._do_log_response(response=response)

        return response

    def __str__(self) -> str:
        """Show object info.

        Returns:
            :obj:`str`
        """
        return "{c.__module__}.{c.__name__}(url={url!r})".format(
            c=self.__class__, url=self.url
        )

    def __repr__(self) -> str:
        """Show object info.

        Returns:
            :obj:`str`
        """
        return self.__str__()

    @property
    def user_agent(self) -> str:
        """Value to use in User-Agent header.

        Returns:
            :obj:`str`: user agent string
        """
        return f"{__name__}.{self.__class__.__name__}/{__version__}"

    def _do_log_request(self, request: requests.PreparedRequest):
        """Do it."""
        if self.log_request_attrs:
            lattrs = ", ".join(self.log_request_attrs).format(
                url=request.url,
                body_size=len(request.body or ""),
                method=request.method,
                headers=self._clean_headers(headers=request.headers),
            )
            self.LOG.debug(f"REQUEST ATTRS: {lattrs}")

        if self.LOG_REQUEST_BODY:
            self.log_body(body=request.body, body_type="REQUEST")

    def _clean_headers(self, headers: dict) -> dict:
        hide = "*********"
        hidden = self.LOG_HIDE_HEADERS
        return {k: hide if k in hidden else v for k, v in headers.items()}

    def _do_log_response(self, response: requests.Response):
        """Do it."""
        if self.log_response_attrs:
            lattrs = ", ".join(self.log_response_attrs).format(
                url=response.url,
                body_size=len(response.text or ""),
                method=response.request.method,
                status_code=response.status_code,
                reason=response.reason,
                elapsed=response.elapsed,
                headers=self._clean_headers(headers=response.headers),
            )
            self.LOG.debug(f"RESPONSE ATTRS: {lattrs}")

        if self.LOG_RESPONSE_BODY:
            self.log_body(body=response.text, body_type="RESPONSE")

    @property
    def log_request_attrs(self) -> List[str]:
        """Get the request attributes that should be logged."""
        return self._get_log_attrs("request")

    @log_request_attrs.setter
    def log_request_attrs(self, value: List[str]):
        """Set the request attributes that should be logged."""
        attr_map = REQUEST_ATTR_MAP
        attr_type = "request"
        self._set_log_attrs(attr_map=attr_map, attr_type=attr_type, value=value)

    @property
    def log_response_attrs(self) -> List[str]:
        """Get the response attributes that should be logged."""
        return self._get_log_attrs("response")

    @log_response_attrs.setter
    def log_response_attrs(self, value: List[str]):
        """Set the response attributes that should be logged."""
        attr_map = RESPONSE_ATTR_MAP
        attr_type = "response"
        self._set_log_attrs(attr_map=attr_map, attr_type=attr_type, value=value)

    def _get_log_attrs(self, attr_type: str) -> List[str]:
        return getattr(self, "_LOG_ATTRS", {}).get(attr_type, [])

    def _set_log_attrs(
        self, attr_map: dict, attr_type: str, value: Union[str, List[str]]
    ):
        if not hasattr(self, "_LOG_ATTRS"):
            self._LOG_ATTRS = {"response": [], "request": []}

        value = [x.lower().strip() for x in listify(value)]

        if not value:
            self._LOG_ATTRS[attr_type] = []
            return

        log_attrs = self._LOG_ATTRS[attr_type]

        if "all" in value:
            for k, v in attr_map.items():
                entry = f"{k}={v}"
                if entry not in log_attrs:
                    log_attrs.append(entry)
            return

        for item in value:
            if item in attr_map:
                value = attr_map[item]
                entry = f"{item}={value}"
                if entry not in log_attrs:
                    log_attrs.append(entry)

    def log_body(self, body: str, body_type: str):
        """Pass."""
        body = body or ""
        body = json_reload(obj=body, error=False, trim=MAX_BODY_LEN)
        self.LOG.debug(f"{body_type} BODY:\n{body}")


class ParserUrl:
    """Parse a URL and ensure it has the neccessary bits."""

    def __init__(self, url: str, default_scheme: str = "https"):
        """Parse a URL and ensure it has the neccessary bits.

        Args:
            url (:obj:`str`): URL to parse
            default_scheme (:obj:`str`, optional): default ``"https"`` - default
                scheme to use if url does not contain a scheme

        Raises:
            :exc:`HttpError`:
                if parsed URL winds up without a hostname, port, or scheme.

        """
        self._init_url: str = url
        """:obj:`str`: initial URL provided"""

        self._init_scheme: str = default_scheme
        """:obj:`str`: default scheme provided"""

        self._init_parsed: ParseResult = urlparse(url)
        """:obj:`urllib.parse.ParseResult`: first pass of parsing URL"""

        self.parsed: ParseResult = self.reparse(
            parsed=self._init_parsed, default_scheme=default_scheme
        )
        """:obj:`urllib.parse.ParseResult`: second pass of parsing URL"""

        for part in ["hostname", "port", "scheme"]:
            if not getattr(self.parsed, part, None):
                error = (
                    f"Parsed URL into {self.parsed_str!r} and no {part!r} provided"
                    f" in URL {url!r}"
                )
                raise HttpError(error)

    def __str__(self) -> str:
        """Show object info.

        Returns:
            :obj:`str`
        """
        cls = self.__class__
        return f"{cls.__module__}.{cls.__name__}({self.parsed_str})"

    def __repr__(self) -> str:
        """Show object info.

        Returns:
            :obj:`str`
        """
        return self.__str__()

    @property
    def hostname(self) -> str:
        """Hostname part from :attr:`ParserUrl.parsed`.

        Returns:
            :obj:`str`: hostname value
        """
        return self.parsed.hostname

    @property
    def port(self) -> int:
        """Port part from :attr:`ParserUrl.parsed`.

        Returns
            :obj:`int`: port value
        """
        return int(self.parsed.port)

    @property
    def scheme(self) -> str:
        """Scheme part from :attr:`ParserUrl.parsed`.

        Returns:
            :obj:`str`: scheme value
        """
        return self.parsed.scheme

    @property
    def url(self) -> str:
        """Get scheme, hostname, and port from :attr:`ParserUrl.parsed`.

        Returns:
            :obj:`str`: schema, hostname, and port unparsed values
        """
        return self.unparse_base(parsed_result=self.parsed)

    @property
    def url_full(self) -> str:
        """Get full URL from :attr:`ParserUrl.parsed`.

        Returns:
            :obj:`str`: full unparsed url
        """
        return self.unparse_all(parsed_result=self.parsed)

    @property
    def parsed_str(self) -> str:
        """Get a str value of :attr:`ParserUrl.parsed`.

        Returns:
            :obj:`str`: str value of :attr:`ParserUrl.parsed`
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

    def make_netloc(self, host: str, port: Union[str, int]) -> str:
        """Create netloc from host and port.

        Args:
            host (:obj:`str`): host part to use in netloc
            port (:obj:`str`): port part to use in netloc

        Returns:
            :obj:`str`: host and port values joined by :

        """
        return ":".join([str(x) for x in [host, port] if x])

    def reparse(self, parsed: ParseResult, default_scheme: str = "") -> ParseResult:
        """Reparse a parsed URL into a parsed URL with values fixed.

        Args:
            parsed (:obj:`urllib.parse.ParseResult`): parsed URL to reparse
            default_scheme (:obj:`str`, optional): default ``""`` -
                default scheme to use if URL does not contain a scheme

        Returns:
            :obj:`urllib.parse.ParseResult`: reparsed result
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
            if ":" in netloc:  # pragma: no cover
                # can't get this to trigger anymore, ignore test coverage
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

        pass2 = urlunparse((scheme, netloc, path, params, query, fragment))
        return urlparse(pass2)

    def unparse_base(self, parsed_result: ParseResult) -> str:
        """Unparse a parsed URL into just the scheme, hostname, and port parts.

        Args:
            parsed (:obj:`urllib.parse.ParseResult`): parsed URL to unparse

        Returns:
            :obj:`str`: unparsed url
        """
        # only unparse self.parsed into url with scheme and netloc
        bits = (parsed_result.scheme, parsed_result.netloc, "", "", "", "")
        return urlunparse(bits)

    def unparse_all(self, parsed_result: ParseResult) -> str:
        """Unparse a parsed URL with all the parts.

        Args:
            parsed (:obj:`urllib.parse.ParseResult`): parsed URL to unparse

        Returns:
            :obj:`str`: unparsed url
        """
        return urlunparse(parsed_result)
