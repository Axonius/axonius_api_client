# -*- coding: utf-8 -*-
"""HTTP client."""
import logging
import pathlib
import warnings
from typing import List, Optional, Union

import requests

from .constants.api import TIMEOUT_CONNECT, TIMEOUT_RESPONSE
from .constants.logs import LOG_LEVEL_HTTP, MAX_BODY_LEN, REQUEST_ATTR_MAP, RESPONSE_ATTR_MAP
from .exceptions import HttpError
from .logs import get_obj_log, set_log_level
from .parsers.url_parser import UrlParser
from .tools import join_url, json_dump, json_load, listify, path_read
from .version import __version__

InsecureRequestWarning = requests.urllib3.exceptions.InsecureRequestWarning


class Http:
    """HTTP client that wraps around around :obj:`requests.Session`."""

    def __init__(
        self,
        url: Union["UrlParser", str],
        certpath: Optional[Union[str, pathlib.Path]] = None,
        certwarn: bool = True,
        certverify: bool = False,
        **kwargs,
    ):
        """HTTP client that wraps around :obj:`requests.Session`.

        Notes:
            * If certpath is supplied, certverify is ignored
            * private key supplied to cert_client_key or cert_client_both
              can **NOT** be password encrypted

        Args:
            url: URL, hostname, or IP address of Axonius instance
            certpath: path to CA bundle file to use when verifying certs offered by :attr:`url`
            certverify: raise exception if cert is self-signed or only if cert is invalid
            certwarn: show insecure warning once or never show insecure warning
            proxy: proxy to use when making https requests to :attr:`url`

        Raises:
            :exc:`HttpError`:

                - if either cert_client_cert or cert_client_key are supplied, and the other is
                  not supplied
                - if any of cert_path, cert_client_cert, cert_client_key, or cert_client_both
                  are supplied and the file does not exist
        """
        self.LOG_LEVEL: Union[str, int] = kwargs.get("log_level", LOG_LEVEL_HTTP)
        """log level for this class ``kwargs=log_level``"""

        self.LOG: logging.Logger = get_obj_log(obj=self, level=self.LOG_LEVEL)
        """Logger for this object."""

        self._MAX_BODY_LEN = MAX_BODY_LEN

        if isinstance(url, UrlParser):
            self.URLPARSED: UrlParser = url
        else:
            self.URLPARSED: UrlParser = UrlParser(url=url, default_scheme="https")

        self.url: str = self.URLPARSED.url
        """URL to connect to"""

        self.SAVE_LAST: bool = kwargs.get("save_last", True)
        """save requests to :attr:`LAST_REQUEST` and responses to :attr:`LAST_RESPONSE`
        ``kwargs=save_last``"""

        self.SAVEHISTORY: bool = kwargs.get("save_history", False)
        """Append all responses to :attr:`HISTORY` ``kwargs=save_history``"""

        self.CONNECT_TIMEOUT: int = kwargs.get("connect_timeout", TIMEOUT_CONNECT)
        """seconds to wait for connections to open to :attr:`url` ``kwargs=connect_timeout``"""

        self.RESPONSE_TIMEOUT: int = kwargs.get("response_timeout", TIMEOUT_RESPONSE)
        """seconds to wait for responses from :attr:`url` ``kwargs=response_timeout``"""

        self.LOG_HIDE_HEADERS: List[str] = ["api-key", "api-secret"]
        """Headers to hide when logging."""

        self.LOG_REQUEST_BODY: bool = kwargs.get("log_request_body", False)
        """Log the full request body ``kwargs=log_request_body``"""

        self.LOG_RESPONSE_BODY: bool = kwargs.get("log_response_body", False)
        """Log the full response body. ``kwargs=log_response_body``"""

        self.HTTP_PROXY: Optional[str] = kwargs.get("http_proxy", None)
        """HTTP proxy to use. ``kwargs=http_proxy``"""

        self.HTTPS_PROXY: Optional[str] = kwargs.get("https_proxy", None)
        """HTTPS proxy to use. ``kwargs=https_proxy``"""

        self.LOG_REQUEST_ATTRS: Optional[List[str]] = kwargs.get("log_request_attrs", None)
        """request attrs to log :attr:`axonius_api_client.constants.logs.REQUEST_ATTR_MAP`
        ``kwargs=log_request_attrs``"""

        self.LOG_RESPONSE_ATTRS: Optional[List[str]] = kwargs.get("log_response_attrs", None)
        """response attrs to log :attr:`axonius_api_client.constants.logs.RESPONSE_ATTR_MAP`
        ``kwargs=log_response_attrs``"""

        self.LOG_LEVEL_URLLIB: str = kwargs.get("log_level_urllib", "warning")
        """logging level for low-level urllib library. ``kwargs=log_level_urllib``"""

        self.CERT_CLIENT_KEY: Optional[Union[str, pathlib.Path]] = kwargs.get(
            "cert_client_key", None
        )
        """Private key file for cert_client_cert ``kwargs=cert_client_key``"""

        self.CERT_CLIENT_CERT: Optional[Union[str, pathlib.Path]] = kwargs.get(
            "cert_client_cert", None
        )
        """cert file to offer to :attr:`url` ``kwargs=cert_client_cert``"""

        self.CERT_CLIENT_BOTH: Optional[Union[str, pathlib.Path]] = kwargs.get(
            "cert_client_both", None
        )
        """cert file with both private key and cert to offer to :attr:`url`
        ``kwargs=cert_client_both``"""

        self.LAST_REQUEST = None
        """:obj:`requests.PreparedRequest`: last request sent"""

        self.LAST_RESPONSE = None
        """:obj:`requests.Response`: last response received"""

        self.HISTORY = []
        """:obj:`list` of :obj:`requests.Response`: all responses received."""

        self.log_request_attrs: Optional[List[str]] = self.LOG_REQUEST_ATTRS
        self.log_response_attrs: Optional[List[str]] = self.LOG_RESPONSE_ATTRS

        self.session: requests.Session = requests.Session()
        """:obj:`requests.Session`: session object to use"""

        headers = kwargs.get("headers") or {}

        self.session.proxies = {}
        self.session.proxies["https"] = self.HTTPS_PROXY
        self.session.proxies["http"] = self.HTTP_PROXY
        self.session.headers.update(headers)

        if certpath:  # pragma: no cover
            path_read(obj=certpath, binary=True)
            self.session.verify = certpath
        else:
            self.session.verify = certverify

        if self.CERT_CLIENT_BOTH:
            path_read(obj=self.CERT_CLIENT_BOTH, binary=True)
            self.session.cert = str(self.CERT_CLIENT_BOTH)
        elif self.CERT_CLIENT_CERT or self.CERT_CLIENT_KEY:
            if not all([self.CERT_CLIENT_CERT, self.CERT_CLIENT_KEY]):
                error = (
                    "You must supply both a 'cert_client_cert' and 'cert_client_key'"
                    " or use 'cert_client_both'!"
                )
                raise HttpError(error)

            path_read(obj=self.CERT_CLIENT_CERT, binary=True)
            path_read(obj=self.CERT_CLIENT_KEY, binary=True)
            self.session.cert = (str(self.CERT_CLIENT_CERT), str(self.CERT_CLIENT_KEY))

        if certwarn is True:
            warnings.simplefilter("once", InsecureRequestWarning)
        elif certwarn is False:
            warnings.simplefilter("ignore", InsecureRequestWarning)

        urllog = logging.getLogger("urllib3.connectionpool")
        set_log_level(obj=urllog, level=self.LOG_LEVEL_URLLIB)

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
        **kwargs,
    ):
        """Create, prepare, and then send a request using :attr:`session`.

        Args:
            path: path to append to :attr:`url`
            route: route to append to :attr:`url`
            method: HTTP method to use
            data: body to send
            params: parameters to url encode
            headers: headers to send
            json: obj to encode as json
            files: files to send
            **kwargs: overrides for object attributes

                * connect_timeout: seconds to wait for connection to open for this request
                * response_timeout: seconds to wait for for response for this request
                * proxies: proxies for this request
                * verify: verification of cert for this request
                * cert: client cert to offer for this request

        Returns:
            :obj:`requests.Response`
        """
        url = join_url(self.url, path, route)

        this_headers = {}
        this_headers.update(headers or {})
        this_headers.setdefault("User-Agent", self.user_agent)

        request = requests.Request(
            url=url,
            method=method,
            data=data,
            headers=this_headers,
            params=params,
            json=json,
            files=files or [],
        )
        prepped_request = self.session.prepare_request(request=request)
        if "Content-Type" not in prepped_request.headers:
            prepped_request.headers["Content-Type"] = "application/vnd.api+json"

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
        """Show object info."""
        return "{c.__module__}.{c.__name__}(url={url!r})".format(c=self.__class__, url=self.url)

    def __repr__(self) -> str:
        """Show object info."""
        return self.__str__()

    @property
    def user_agent(self) -> str:
        """Value to use in User-Agent header."""
        return f"{__name__}.{self.__class__.__name__}/{__version__}"

    def _do_log_request(self, request):
        """Log attributes and/or body of a request.

        Args:
            request (:obj:`requests.PreparedRequest`): prepared request to log attrs/body of
        """
        if self.log_request_attrs:
            lattrs = ", ".join(self.log_request_attrs).format(
                url=request.url,
                body_size=len(request.body or ""),
                method=request.method,
                headers=self._clean_headers(headers=request.headers),
            )
            self.LOG.debug(f"REQUEST ATTRS: {lattrs}")

        if self.LOG_REQUEST_BODY:
            self.log_body(body=request.body, body_type="REQUEST", src=request)

    def _clean_headers(self, headers: dict) -> dict:
        """Clean headers with sensitive information.

        Args:
            headers: headers to clean values of
        """
        hide = "*********"
        hidden = self.LOG_HIDE_HEADERS
        return {k: hide if k in hidden else v for k, v in headers.items()}

    def _do_log_response(self, response):
        """Log attributes and/or body of a response.

        Args:
            response (:obj:`requests.Response`): response to log attrs/body of
        """
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
            self.log_body(body=response.text, body_type="RESPONSE", src=response)

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
        """Get the log attributes for a specific type.

        Args:
            attr_type: 'request' or 'response'
        """
        return getattr(self, "_LOG_ATTRS", {}).get(attr_type, [])

    def _set_log_attrs(self, attr_map: dict, attr_type: str, value: Union[str, List[str]]):
        """Set the log attributes for a specific type.

        Args:
            attr_map: map of attributes to format strings
            attr_type: 'request' or 'response'
            value: user supplied attrs to log
        """
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

    def log_body(self, body: str, body_type: str, src=None):
        """Log a request or response body.

        Args:
            body: content to log
            body_type: 'request' or 'response'
        """
        trim = self._MAX_BODY_LEN
        body = body or ""
        body = json_load(obj=body, error=False)

        if not isinstance(body, (str, int, float, type(None), bytes)):
            body = json_dump(obj=body, error=False)

        if isinstance(body, bytes):
            body = body.decode()

        if isinstance(body, str):
            body = body.strip()

            if trim and len(body) >= trim:
                body = body[:trim] + f"\nTrimmed over {trim} characters"

        self.LOG.debug(f"{body_type} BODY:\n{body}")
