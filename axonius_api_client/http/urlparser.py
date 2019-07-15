# -*- coding: utf-8 -*-
"""URL parser module."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six

from . import exceptions


class UrlParser(object):
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
        """Hostname part from :attr:`UrlParser.parsed`.

        Returns:
            :obj:`str`

        """
        return self.parsed.hostname

    @property
    def port(self):
        """Port part from :attr:`UrlParser.parsed`.

        Returns
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
        return self.unparse_base(parsed_result=self.parsed)

    @property
    def url_full(self):
        """Get full URL from :attr:`UrlParser.parsed`.

        Returns:
            :obj:`str`

        """
        return self.unparse_all(parsed_result=self.parsed)

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
