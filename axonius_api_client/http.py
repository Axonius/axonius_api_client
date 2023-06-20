"""HTTP client."""
import logging
import pathlib
import typing as t
import warnings

import OpenSSL  # noqa: TCH002
import requests
import requests.cookies
import requests.structures
import urllib3
import urllib3.exceptions

from . import version
from .constants.api import TIMEOUT_CONNECT, TIMEOUT_RESPONSE
from .constants.ctypes import PathLike, PatternLikeListy
from .constants.logs import (
    LOG_LEVEL_HTTP,
    MAX_BODY_LEN,
    REQUEST_ATTR_MAP,
    RESPONSE_ATTR_MAP,
)
from .exceptions import HttpError
from .logs import get_obj_log, set_log_level
from .projects import cert_human
from .projects.cf_token import constants as cf_constants
from .projects.cf_token.flows import flow_get_token
from .projects.cf_token.tools import get_env_url, is_url
from .projects.url_parser import UrlParser
from .setup_env import get_env_user_agent
from .tools import (
    coerce_bool,
    coerce_int_float,
    coerce_str,
    join_url,
    json_log,
    listify,
    path_read,
    tilde_re,
)

INJECT_RESULTS: t.Tuple[
    bool,
    t.List[str],
] = cert_human.ssl_capture.inject_into_urllib3()
T_Cookies: t.Type = t.Union[dict, requests.cookies.RequestsCookieJar]
T_Headers: t.Type = t.Union[dict, requests.structures.CaseInsensitiveDict]

HIDE_HEADERS: t.Tuple[str, ...] = (
    "~cookie",
    "~auth",
    "~token",
    "~^cf_",
    "~secret",
    "~key",
    "~username",
    "~password",
)


def is_headers(value: t.Any) -> bool:
    """Check if token is a valid headers object."""
    return isinstance(value, (dict, requests.structures.CaseInsensitiveDict))


def is_cookies(value: t.Any) -> bool:
    """Check if token is a valid cookies object."""
    return isinstance(value, (dict, requests.cookies.RequestsCookieJar))


class Http:
    """HTTP client that wraps around :obj:`requests.Session`."""

    session: requests.Session = None
    """Requests session object."""

    LOG: logging.Logger = None
    """Logger for this object."""

    HISTORY: t.List[requests.Response] = None
    """History of all requests made."""

    LAST_REQUEST: t.Optional[requests.PreparedRequest] = None
    """Last request made."""

    LAST_RESPONSE: t.Optional[requests.Response] = None
    """Last response received."""

    SAVE_HISTORY: bool = False
    """Save history of requests."""

    SAVE_LAST: bool = True
    """Save last request and response."""

    URLPARSED: UrlParser = None
    """Parsed URL object."""

    url: str = None
    """URL to use for requests."""

    CERT_PATH: t.Optional[PathLike] = None
    """Path to CA cert file."""

    CERT_WARN: bool = True
    """Warn if CA cert is not found."""

    CERT_VERIFY: bool = False
    """Verify server cert."""

    HTTP_HEADERS: t.Optional[T_Headers] = None
    """Headers to use for all requests."""

    HTTP_COOKIES: t.Optional[T_Cookies] = None
    """Cookies to use for all requests."""

    CERT_CLIENT_BOTH: t.Optional[PathLike] = None
    """Path to client cert and key file."""

    CERT_CLIENT_CERT: t.Optional[PathLike] = None
    """Path to client cert file."""

    CERT_CLIENT_KEY: t.Optional[PathLike] = None
    """Path to client key file."""

    CONNECT_TIMEOUT: t.Optional[t.Union[int, float]] = TIMEOUT_CONNECT
    """Timeout for connecting to server."""

    RESPONSE_TIMEOUT: t.Optional[t.Union[int, float]] = TIMEOUT_RESPONSE
    """Timeout for receiving response from server."""

    HTTP_PROXY: t.Optional[str] = None
    """Proxy to use for HTTP requests."""

    HTTPS_PROXY: t.Optional[str] = None
    """Proxy to use for HTTPS requests."""

    LOG_BODY_LINES: int = MAX_BODY_LEN
    """Max length of request and response bodies to log."""

    LOG_HIDE_HEADERS: t.Optional[PatternLikeListy] = HIDE_HEADERS
    """Headers to hide when logging."""

    LOG_HIDE_STR: str = "*********"
    """String to use to hide sensitive data in logs."""

    LOG_LEVEL: t.Union[int, str] = LOG_LEVEL_HTTP
    """Log level to use for this object."""

    LOG_LEVEL_URLLIB: t.Union[int, str] = "warning"
    """Log level to use for urllib3."""

    LOG_REQUEST_ATTRS: t.Optional[t.List[str]] = None
    """Attributes of request to log."""

    LOG_REQUEST_BODY: bool = False
    """Log request body."""

    LOG_RESPONSE_ATTRS: t.Optional[t.List[str]] = None
    """Attributes of response to log."""

    LOG_RESPONSE_BODY: bool = False
    """Log response body."""

    URL_CERT: t.Optional[cert_human.Cert] = None
    """Cert object for URL."""

    URL_CERT_CHAIN: t.Optional[t.List[cert_human.Cert]] = None
    """Cert chain for URL."""

    CLIENT: t.Optional[object] = None
    """Client object that created this object."""
    # TBD: Connect needs an interface for proper type hinting without circular reference

    def __init__(  # noqa: PLR0913
        self,
        url: t.Union[UrlParser, str],
        certpath: t.Optional[PathLike] = None,
        certwarn: bool = CERT_WARN,
        certverify: bool = CERT_VERIFY,
        headers: t.Optional[T_Headers] = None,
        cookies: t.Optional[T_Cookies] = None,
        cert_client_both: t.Optional[PathLike] = None,
        cert_client_cert: t.Optional[PathLike] = None,
        cert_client_key: t.Optional[PathLike] = None,
        connect_timeout: t.Optional[t.Union[int, float]] = CONNECT_TIMEOUT,
        response_timeout: t.Optional[t.Union[int, float]] = RESPONSE_TIMEOUT,
        http_proxy: t.Optional[str] = None,
        https_proxy: t.Optional[str] = None,
        log_body_lines: int = LOG_BODY_LINES,
        log_hide_headers: t.Optional[PatternLikeListy] = HIDE_HEADERS,
        log_hide_str: t.Optional[str] = LOG_HIDE_STR,
        log_level: t.Union[int, str] = LOG_LEVEL,
        log_level_urllib: t.Union[int, str] = LOG_LEVEL_URLLIB,
        log_request_attrs: t.Optional[t.Union[str, t.Iterable[str]]] = None,
        log_request_body: bool = LOG_REQUEST_BODY,
        log_response_attrs: t.Optional[t.Union[str, t.Iterable[str]]] = None,
        log_response_body: bool = LOG_RESPONSE_BODY,
        save_history: bool = SAVE_HISTORY,
        save_last: bool = SAVE_LAST,
        cf_token: t.Optional[str] = None,
        cf_url: t.Optional[str] = None,
        cf_path: t.Optional[PathLike] = cf_constants.CF_PATH,
        cf_run: bool = cf_constants.CLIENT_RUN,
        cf_run_login: bool = cf_constants.FLOW_RUN_LOGIN,
        cf_run_access: bool = cf_constants.FLOW_RUN_ACCESS,
        cf_env: bool = cf_constants.FLOW_ENV,
        cf_echo: bool = cf_constants.FLOW_ECHO,
        cf_echo_verbose: bool = cf_constants.FLOW_ECHO_VERBOSE,
        cf_error: bool = cf_constants.CLIENT_ERROR,
        cf_error_login: bool = cf_constants.FLOW_ERROR,
        cf_error_access: bool = cf_constants.FLOW_ERROR,
        cf_timeout_access: t.Optional[int] = cf_constants.TIMEOUT_ACCESS,
        cf_timeout_login: t.Optional[int] = cf_constants.TIMEOUT_LOGIN,
        **kwargs,
    ) -> None:
        """HTTP client that wraps around :obj:`requests.Session`.

        Notes:
            * If certpath is supplied, certverify is ignored
            * private key supplied to cert_client_key or cert_client_both
              can **NOT** be password encrypted

        Args:
            url: URL, hostname, or IP address of Axonius instance
            certpath: token to CA bundle file to use when verifying certs offered by :attr:`url`
            certwarn: show insecure warning once or never show insecure warning
            certverify: raise exception if cert is self-signed or only if cert is invalid
            headers: headers to send with every request
            cookies: cookies to send with every request
            log_level: log level to use for this object
            log_body_lines: max length of request and response bodies to log
            log_hide_headers: headers to hide when logging
            log_hide_str: string to use to hide sensitive data in logs
            log_request_attrs: attributes of request to log
            log_response_attrs: attributes of response to log
            save_last: save last request and response to :attr:`last_request` and
                :attr:`last_response`
            save_history: save all requests and responses to :attr:`history`
            connect_timeout: seconds to wait for connections to open to :attr:`url`
            response_timeout: seconds to wait for responses from :attr:`url`
            log_request_body: log the request body
            log_response_body: log the response body
            http_proxy: proxy to use when making http requests to :attr:`url`
            https_proxy: proxy to use when making https requests to :attr:`url`
            log_level_urllib: log level to use for urllib3
            cert_client_key: path to client private key file
            cert_client_both: path to client private key and cert file
            cert_client_cert: path to client cert file
            cf_url: URL to use in `access token` and `access login` commands,
                will fallback to url if not supplied
            cf_token: access token supplied by user, will be checked for validity if not empty
            cf_env: if no token supplied, try to get token from OS env var CF_TOKEN
            cf_run: if no token supplied or in OS env vars, try to get token from `access token` and
                `access login` commands
            cf_run_access: if run is True, try to get token from `access token`,
            cf_run_login: if run is True and no token returned from `access token` command,
                try to get token from `access login` command
            cf_path: path to cloudflared binary to run, can be full path or path in OS env var $PATH
            cf_timeout_access: timeout for `access token` command in seconds
            cf_timeout_login: timeout for `access login` command in seconds
            cf_error: raise error if an invalid token is found or no token can be found
            cf_error_access: raise exc if `access token` command fails and login is False
            cf_error_login: raise exc if `access login` command fails
            cf_echo: echo commands and results to stdout
            cf_echo_verbose: echo checks to stdout
            **kwargs: no longer used, will throw a deprecation warning

        Raises:
            :exc:`HttpError`:
                - if either cert_client_cert or cert_client_key are supplied, and the other is
                  not supplied
                - if any of cert_path, cert_client_cert, cert_client_key, or cert_client_both
                  are supplied and the file does not exist
        """
        self.KWARGS: dict = kwargs
        self.session = requests.Session()
        self.LOG_LEVEL: t.Union[int, str] = log_level
        self.LOG: logging.Logger = get_obj_log(obj=self, level=self.LOG_LEVEL)

        self.HISTORY: t.List[requests.Response] = []
        self.LAST_REQUEST: t.Optional[requests.PreparedRequest] = None
        self.LAST_RESPONSE: t.Optional[requests.Response] = None

        self.LOG_BODY_LINES: t.Optional[int] = coerce_int_float(
            log_body_lines,
            error=False,
        )
        self.LOG_HIDE_HEADERS: PatternLikeListy = tilde_re(listify(log_hide_headers))
        self.LOG_HIDE_STR: t.Optional[str] = log_hide_str
        self.LOG_LEVEL_URLLIB: str = log_level_urllib
        self.LOG_REQUEST_BODY: bool = coerce_bool(log_request_body)
        self.LOG_RESPONSE_BODY: bool = coerce_bool(log_response_body)

        self.log_request_attrs = log_request_attrs
        self.log_response_attrs = log_response_attrs

        self.URLPARSED: UrlParser = self.parse_url(url=url)
        self.url: str = self.URLPARSED.url

        self.HTTP_HEADERS: T_Headers = headers if is_headers(headers) else {}
        self.HTTP_COOKIES: T_Cookies = cookies if is_cookies(cookies) else {}

        if cf_token or cf_env or cf_run:
            self.set_cf_token(
                url=cf_url,
                token=cf_token,
                run=cf_run,
                path=cf_path,
                run_login=cf_run_login,
                run_access=cf_run_access,
                env=cf_env,
                echo=cf_echo,
                echo_verbose=cf_echo_verbose,
                error=cf_error,
                error_login=cf_error_login,
                error_access=cf_error_access,
                timeout_access=cf_timeout_access,
                timeout_login=cf_timeout_login,
            )

        self.CERT_PATH: t.Optional[PathLike] = certpath
        self.CERT_WARN: bool = coerce_bool(certwarn)
        self.CERT_VERIFY: bool = certverify

        self.CERT_CLIENT_BOTH: t.Optional[PathLike] = cert_client_both
        self.CERT_CLIENT_CERT: t.Optional[PathLike] = cert_client_cert
        self.CERT_CLIENT_KEY: t.Optional[PathLike] = cert_client_key

        self.CONNECT_TIMEOUT: t.Optional[t.Union[int, float]] = coerce_int_float(
            connect_timeout,
            error=False,
        )
        self.RESPONSE_TIMEOUT: t.Optional[t.Union[int, float]] = coerce_int_float(
            response_timeout,
            error=False,
        )

        self.HTTP_PROXY: t.Optional[str] = http_proxy
        self.HTTPS_PROXY: t.Optional[str] = https_proxy

        self.SAVE_HISTORY: bool = coerce_bool(save_history)
        self.SAVE_LAST: bool = coerce_bool(save_last)

        self.set_urllib_warnings()
        self.set_urllib_log()
        self.new_session()
        self._init()

    def set_cf_token(
        self,
        url: t.Optional[str] = None,
        token: t.Optional[str] = None,
        env: bool = cf_constants.FLOW_ENV,
        run: bool = cf_constants.FLOW_RUN,
        run_access: bool = cf_constants.FLOW_RUN_ACCESS,
        run_login: bool = cf_constants.FLOW_RUN_LOGIN,
        path: t.Union[str, bytes, pathlib.Path] = cf_constants.CF_PATH,
        timeout_access: t.Optional[int] = cf_constants.TIMEOUT_ACCESS,
        timeout_login: t.Optional[int] = cf_constants.TIMEOUT_LOGIN,
        error: bool = cf_constants.FLOW_ERROR,
        error_access: bool = cf_constants.FLOW_ERROR,
        error_login: bool = cf_constants.FLOW_ERROR,
        echo: bool = cf_constants.FLOW_ECHO,
        echo_verbose: bool = cf_constants.FLOW_ECHO_VERBOSE,
    ) -> t.Optional[str]:
        """Set the Cloudflare access token to use for requests.

        Notes:
            - If `token` is supplied, it will be checked for validity
            - If `token` is not supplied, and `env` is True, try to get a token
              from the OS environment variables CF_TOKEN or AX_TOKEN
            - If `token` is not supplied or defined in OS environment variables
              and `run` is True, try to get a token from the command `$path access token`
            - If `token` is not supplied or defined in OS environment variables
              or returned from the command `$path access token` and `login` is True,
              try to get a token from the command `$path access login`

        Args:
            url: URL to use in `access token` and `access login` commands,
                will default to self.url if not supplied
            token: access token supplied by user, will be checked for validity if not empty
            env: if no token supplied, try to get token from OS env var CF_TOKEN
            run: if no token supplied or in OS env vars, try to get token from `access token` and
                `access login` commands
            run_access: if run is True, try to get token from `access token`,
            run_login: if run is True and no token returned from `access token` command, try to get
                token from `access login` command
            path: path to cloudflared binary to run, can be full path or path in OS env var $PATH
            timeout_access: timeout for `access token` command in seconds
            timeout_login: timeout for `access login` command in seconds
            error: raise error if an invalid token is found or no token can be found
            error_access: raise exc if `access token` command fails and login is False
            error_login: raise exc if `access login` command fails
            echo: echo commands and results to stdout
            echo_verbose: echo checks to stdout

        Returns:
            None or token, depending on `error` and `error_access` and `error_login`
        """
        url = (
            url
            if is_url(url)
            else get_env_url(error=True, error_empty=False) or self.url
        )
        token = flow_get_token(
            url=url,
            path=path,
            timeout_access=timeout_access,
            timeout_login=timeout_login,
            error=error,
            error_access=error_access,
            error_login=error_login,
            token=token,
            env=env,
            run=run,
            run_login=run_login,
            run_access=run_access,
            echo=echo,
            echo_verbose=echo_verbose,
        )
        self.HTTP_HEADERS["cf-access-token"] = token
        self.session.headers["cf-access-token"] = token
        return token

    def safe_request(
        self,
        error: bool = False,
        **kwargs,
    ) -> t.Optional[requests.Response]:
        """Make a request, but catch all exceptions and return None."""
        kwargs.setdefault("verify", False)
        kwargs.setdefault("connect_timeout", 10)
        kwargs.setdefault("response_timeout", 10)
        # noinspection PyBroadException
        try:
            return self(**kwargs)
        except Exception:  # pragma: no cover  # noqa: BLE001
            if error:
                raise
        return None  # pragma: no cover

    def get_cert(self, error: bool = False) -> t.Optional[cert_human.Cert]:
        """Get the SSL certificate from url."""
        if not isinstance(self.URL_CERT, cert_human.Cert):
            response: t.Optional[requests.Response] = self.safe_request(error=error)
            value = None
            if response:
                cert: OpenSSL.crypto.X509 = response.raw.captured_cert
                source: dict = {"url": self.url, "method": f"{self.get_cert.__name__}"}
                value = cert_human.Cert(cert=cert, source=source)
            self.URL_CERT = value
        return self.URL_CERT

    def get_cert_chain(self, error: bool = False) -> t.List[cert_human.Cert]:
        """Get the SSL certificate chain from url."""
        if not (isinstance(self.URL_CERT_CHAIN, list) and self.URL_CERT_CHAIN):
            response: t.Optional[requests.Response] = self.safe_request(error=error)
            value = []
            if response:
                chain: t.List[OpenSSL.crypto.X509] = listify(
                    response.raw.captured_chain,
                )
                source: dict = {
                    "url": self.url,
                    "method": f"{self.get_cert_chain.__name__}",
                }
                value = [cert_human.Cert(cert=x, source=source) for x in chain]
            self.URL_CERT_CHAIN = value
        return self.URL_CERT_CHAIN

    def parse_url(self, url: t.Union[str, UrlParser]) -> UrlParser:
        """Pass."""
        if isinstance(url, UrlParser):
            ret = url
            self.LOG.debug(f"Using supplied {ret}")
        else:
            ret = UrlParser(url=url, default_scheme="https")
            self.LOG.debug(f"Parsed {url} into {ret}")
        return ret

    def new_session(self):
        """Create a new session object."""
        self.session: requests.Session = requests.Session()
        self.set_session_headers()
        self.set_session_cookies()
        self.set_session_proxies()
        self.set_session_verify()
        self.set_session_cert()

    def set_session_headers(self):
        """Configure :attr:`session` headers with :attr:`HTTP_HEADERS`."""
        self.session.headers.update(self.HTTP_HEADERS)

    def set_session_cookies(self):
        """Configure :attr:`session` cookies with :attr:`HTTP_COOKIES`."""
        self.session.cookies.update(self.HTTP_COOKIES)

    def set_session_proxies(self):
        """Configure :attr:`session` proxies."""
        self.session.proxies = {"https": self.HTTPS_PROXY, "http": self.HTTP_PROXY}

    def set_session_verify(self):
        """Configure :attr:`session` verify with a cert bundle or a bool."""
        if self.CERT_PATH:  # pragma: no cover
            # TBD: verify cert bundle
            self.CERT_PATH, _ = path_read(obj=self.CERT_PATH, binary=True)
            self.LOG.debug(f"Resolved cert verify to {self.CERT_PATH}")
            self.session.verify = str(self.CERT_PATH)
        else:
            self.session.verify = self.CERT_VERIFY
            self.LOG.debug(f"Resolved cert verify to {self.CERT_VERIFY}")

    def set_session_cert(self):
        """Configure :attr:`session` with the client cert."""
        if self.CERT_CLIENT_BOTH:
            # TBD: verify cert and key
            self.CERT_CLIENT_BOTH, _ = path_read(obj=self.CERT_CLIENT_BOTH, binary=True)
            self.LOG.debug(
                f"Resolved client cert with both cert and key to {self.CERT_CLIENT_BOTH}",
            )
            self.session.cert = str(self.CERT_CLIENT_BOTH)

        if (self.CERT_CLIENT_CERT or self.CERT_CLIENT_KEY) and not (
            self.CERT_CLIENT_CERT and self.CERT_CLIENT_KEY
        ):
            msg = "Must supply 'cert_client_cert' and 'cert_client_key' or 'cert_client_both'"
            raise HttpError(
                msg,
            )

        if self.CERT_CLIENT_CERT and self.CERT_CLIENT_KEY:
            # TBD: verify cert and key
            self.CERT_CLIENT_CERT, _ = path_read(obj=self.CERT_CLIENT_CERT, binary=True)
            self.LOG.debug(
                f"Resolved client cert with cert only to {self.CERT_CLIENT_CERT}",
            )

            self.CERT_CLIENT_KEY, _ = path_read(obj=self.CERT_CLIENT_KEY, binary=True)
            self.LOG.debug(
                f"Resolved client cert with key only to {self.CERT_CLIENT_KEY}",
            )
            self.session.cert = (str(self.CERT_CLIENT_CERT), str(self.CERT_CLIENT_KEY))

    def set_urllib_warnings(self):
        """Filter urllib warnings to show once or ignore.

        Notes:
            if self.CERT_WARN is True, show warning once
            if self.CERT_WARN is False, ignore warning
        """
        if self.CERT_WARN is True:
            warnings.simplefilter("once", urllib3.exceptions.InsecureRequestWarning)
        elif self.CERT_WARN is False:
            warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)

    def set_urllib_log(self):
        """Set the urllib3 logging level to :attr:`LOG_LEVEL_URLLIB`."""
        set_log_level(
            obj=logging.getLogger("urllib3.connectionpool"),
            level=self.LOG_LEVEL_URLLIB,
        )

    def __call__(
        self,
        path: t.Optional[str] = None,
        route: t.Optional[str] = None,
        method: str = "get",
        data: t.Optional[str] = None,
        params: t.Optional[dict] = None,
        headers: t.Optional[dict] = None,
        cookies: t.Optional[dict] = None,
        json: t.Optional[dict] = None,
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
            cookies: cookies to send
            json: obj to encode as json
            files: files to send
            **kwargs: overrides for object attributes

                * connect_timeout: seconds to wait for connection to open for this request
                * response_timeout: seconds to wait for response for this request
                * proxies: proxies for this request
                * verify: verification of cert for this request
                * cert: client cert to offer for this request

        Returns:
            :obj:`requests.Response`
        """

        def log_if_headers(msg: str):  # pragma: no cover
            """Pass."""
            if "headers" in self.log_request_attrs:
                self.LOG.debug(msg)

        session_reset = kwargs.get("session_reset", False)
        if not hasattr(self, "session") or session_reset is True:  # pragma: no cover
            self.new_session()

        url = join_url(self.url, path, route)

        this_headers = {}
        this_headers.update(headers or {})
        this_headers.setdefault("User-Agent", self.user_agent)

        timeout = (
            kwargs.get("connect_timeout", self.CONNECT_TIMEOUT),
            kwargs.get("response_timeout", self.RESPONSE_TIMEOUT),
        )

        request = requests.Request(
            url=url,
            method=method,
            data=data,
            headers=this_headers,
            cookies=cookies or {},
            params=params,
            json=json,
            files=files or [],
        )
        prepped_request = self.session.prepare_request(request=request)

        # TBD: this should be in apiendpoints
        if "Content-Type" not in prepped_request.headers:
            prepped_request.headers["Content-Type"] = "application/vnd.api+json"

        if self.SAVE_LAST:
            self.LAST_REQUEST = prepped_request

        self._do_log_request(request=prepped_request)

        pre_send_args = {
            "proxies": kwargs.get("proxies", self.session.proxies),
            "stream": kwargs.get("stream", self.session.stream),
            "verify": kwargs.get("verify", self.session.verify),
            "cert": kwargs.get("cert", self.session.cert),
        }
        log_if_headers(f"Request arguments before environment merge: {pre_send_args}")

        send_args = self.session.merge_environment_settings(
            url=prepped_request.url,
            **pre_send_args,
        )
        log_if_headers(f"Request arguments after environment merge: {send_args}")

        response = self.session.send(
            request=prepped_request,
            timeout=timeout,
            **send_args,
        )

        if self.SAVE_LAST:
            self.LAST_RESPONSE = response

        if self.SAVE_HISTORY:
            self.HISTORY.append(response)

        self._do_log_response(response=response)

        return response

    def __str__(self) -> str:
        """Show object info."""
        return "{c.__module__}.{c.__name__}(url={url!r})".format(
            c=self.__class__,
            url=self.url,
        )

    def __repr__(self) -> str:
        """Show object info."""
        return self.__str__()

    @property
    def user_agent(self) -> str:
        """Value to use in User-Agent header."""
        ver = version.__version__
        return get_env_user_agent() or f"{__name__}.{self.__class__.__name__}/{ver}"

    def _do_log_request(self, request):
        """Log attributes and/or body of a request.

        Args:
            request (:obj:`requests.PreparedRequest`): prepared request to log attrs/body of
        """
        if self.log_request_attrs:
            cookies = getattr(request, "_cookies", {})
            headers = getattr(request, "headers", {})
            lattrs = ", ".join(self.log_request_attrs).format(
                url=request.url,
                body_size=len(request.body or ""),
                method=request.method,
                headers=self._clean_headers(headers=headers),
                cookies=self._clean_headers(headers=cookies),
            )
            self.LOG.debug(f"REQUEST ATTRS: {lattrs}")

        if self.LOG_REQUEST_BODY:
            self.LOG.debug(
                self.log_body(body=request.body, body_type="REQUEST", src=request),
            )

    def _clean_headers(self, headers: dict) -> dict:
        """Clean headers with sensitive information.

        Args:
            headers: headers to clean values of
        """

        def getval(key, value):
            """Pass."""
            if isinstance(self.LOG_HIDE_STR, str) and self.LOG_HIDE_STR:
                skey = str(key).lower()
                for check in self.LOG_HIDE_HEADERS:
                    if (isinstance(check, str) and check.lower() == skey) or (
                        isinstance(check, t.Pattern) and check.search(key)
                    ):
                        return self.LOG_HIDE_STR
            return value

        # noinspection PyBroadException
        try:
            return {k: getval(k, v) for k, v in headers.items()}
        except Exception:  # pragma: no cover  # noqa: BLE001
            return headers

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
                cookies=self._clean_headers(headers=response.cookies),
            )
            self.LOG.debug(f"RESPONSE ATTRS: {lattrs}")

        if self.LOG_RESPONSE_BODY:
            self.LOG.debug(
                self.log_body(body=response.text, body_type="RESPONSE", src=response),
            )

    @property
    def log_request_attrs(self) -> t.List[str]:
        """Get the request attributes that should be logged."""
        return self._get_log_attrs("request")

    @log_request_attrs.setter
    def log_request_attrs(self, value: t.List[str]):
        """Set the request attributes that should be logged."""
        attr_map = REQUEST_ATTR_MAP
        attr_type = "request"
        self._set_log_attrs(attr_map=attr_map, attr_type=attr_type, value=value)

    @property
    def log_response_attrs(self) -> t.List[str]:
        """Get the response attributes that should be logged."""
        return self._get_log_attrs("response")

    @log_response_attrs.setter
    def log_response_attrs(self, value: t.List[str]):
        """Set the response attributes that should be logged."""
        attr_map = RESPONSE_ATTR_MAP
        attr_type = "response"
        self._set_log_attrs(attr_map=attr_map, attr_type=attr_type, value=value)

    def _get_log_attrs(self, attr_type: str) -> t.List[str]:
        """Get the log attributes for a specific type.

        Args:
            attr_type: 'request' or 'response'
        """
        return getattr(self, "_LOG_ATTRS", {}).get(attr_type, [])

    def _set_log_attrs(
        self,
        attr_map: dict,
        attr_type: str,
        value: t.Union[str, t.List[str]],
    ):
        """Set the log attributes for a specific type.

        Args:
            attr_map: map of attributes to format strings
            attr_type: 'request' or 'response'
            value: user supplied attrs to log
        """
        if not hasattr(self, "_LOG_ATTRS"):
            self._LOG_ATTRS = {"response": [], "request": []}

        value = [x.lower().strip() for x in listify(value) if isinstance(x, str)]

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

    def log_body(
        self,
        body: t.Any,
        body_type: str,
        src: t.Optional[t.Any] = None,
    ) -> str:
        """Get a string for logging a request or response body.

        Args:
            body: content to log
            body_type: 'request' or 'response'
            src: source of the body

        """
        body = json_log(obj=coerce_str(value=body), trim=self.LOG_BODY_LINES)
        return f"{body_type} BODY from {src}:\n{body}"

    def _init(self):
        """Pass."""
