# -*- coding: utf-8 -*-
"""HTTP client."""
from typing import Union
from urllib.parse import urlparse, urlunparse

from ..exceptions import HttpError


class UrlParser:
    """Parse a URL and ensure it has the neccessary bits."""

    def __init__(self, url: str, default_scheme: str = "https"):
        """Parse a URL and ensure it has the neccessary bits.

        Args:
            url: URL to parse
            default_scheme: scheme to use if url does not contain a scheme

        Raises:
            :exc:`HttpError`: if parsed URL winds up without a hostname, port, or scheme.
        """
        self.INIT_URL: str = url
        """initial URL provided"""

        self.INIT_SCHEME: str = default_scheme
        """default scheme provided"""

        self.INIT_PARSED = urlparse(url)
        """:obj:`urllib.parse.ParseResult`: first pass of parsing URL"""

        self.parsed = self.reparse(parsed=self.INIT_PARSED, default_scheme=default_scheme)
        """:obj:`urllib.parse.ParseResult`:second pass of parsing URL"""

        for part in ["hostname", "port", "scheme"]:
            if not getattr(self.parsed, part, None):
                error = (
                    f"Parsed URL into {self.parsed_str!r} and no {part!r} provided"
                    f" in URL {url!r}"
                )
                raise HttpError(error)

    def __str__(self) -> str:
        """Show object info."""
        cls = self.__class__
        return f"{cls.__module__}.{cls.__name__}({self.parsed_str})"

    def __repr__(self) -> str:
        """Show object info."""
        return self.__str__()

    @property
    def hostname(self) -> str:
        """Hostname part from :attr:`UrlParser.parsed`."""
        return self.parsed.hostname

    @property
    def port(self) -> int:
        """Port part from :attr:`UrlParser.parsed`."""
        return int(self.parsed.port)

    @property
    def scheme(self) -> str:
        """Scheme part from :attr:`UrlParser.parsed`."""
        return self.parsed.scheme

    @property
    def url(self) -> str:
        """Get scheme, hostname, and port from :attr:`UrlParser.parsed`."""
        return self.unparse_base(parsed_result=self.parsed)

    @property
    def url_full(self) -> str:
        """Get full URL from :attr:`UrlParser.parsed`."""
        return self.unparse_all(parsed_result=self.parsed)

    @property
    def parsed_str(self) -> str:
        """Get a str value of :attr:`UrlParser.parsed`."""
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
            hosthost: hostname to use in netloc
            portport: port to use in netloc
        """
        return ":".join([str(x) for x in [host, port] if x])

    def reparse(self, parsed, default_scheme: str = ""):
        """Reparse a parsed URL into a parsed URL with values fixed.

        Args:
            parsed (:obj:`urllib.parse.ParseResult`): parsed URL to reparse
            default_scheme: default scheme to use if URL does not contain a scheme

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

    def unparse_base(self, parsed_result) -> str:
        """Unparse a parsed URL into just the scheme, hostname, and port parts.

        Args:
            parsed (:obj:`urllib.parse.ParseResult`): parsed URL to unparse
        """
        # only unparse self.parsed into url with scheme and netloc
        bits = (parsed_result.scheme, parsed_result.netloc, "", "", "", "")
        return urlunparse(bits)

    def unparse_all(self, parsed_result) -> str:
        """Unparse a parsed URL with all the parts.

        Args:
            parsed (:obj:`urllib.parse.ParseResult`): parsed URL to unparse
        """
        return urlunparse(parsed_result)
