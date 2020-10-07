# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.http."""

import pytest

from axonius_api_client.exceptions import HttpError
from axonius_api_client.parsers.url_parser import UrlParser


class TestUrlParser:
    """Test UrlParser."""

    def test_schemehostport443(self):
        """Test a proper URL gets parsed the same."""
        u = UrlParser("https://host:443/blah")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"
        assert u.parsed.path == "/blah"
        assert u.url_full == "https://host:443/blah"
        assert u.url == "https://host:443"

    def test_str_repr(self):
        """Test str/repr has URL path."""
        u = UrlParser("https://host:443/blah")
        assert u.parsed.path in format(u)
        assert u.parsed.path in repr(u)

    def test_schemehost_noport443(self):
        """Test port gets added for https scheme."""
        u = UrlParser("https://host")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_justhost(self):
        """Test schema added for just host."""
        u = UrlParser("host")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_justhostport(self):
        """Test schema added for just host and port."""
        u = UrlParser("host:443")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_host_noschemeport(self):
        """Test exc when no port or scheme in URL."""
        exc = HttpError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            UrlParser("host", default_scheme="")

    def test_unknownschemehost_noport(self):
        """Test exc when no port and non http/https scheme."""
        exc = HttpError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            UrlParser("httpx://host")

    def test_hostport443_withslash(self):
        """Test scheme added with port 443 and no scheme in URL."""
        u = UrlParser("host:443/")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_hostport443_noscheme(self):
        """Test scheme added with port 443 and no scheme in URL."""
        u = UrlParser("host:443", default_scheme="")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_hostport80_noscheme(self):
        """Test scheme added with port 80 and no scheme in URL."""
        u = UrlParser("host:80", default_scheme="")
        assert u.hostname == "host"
        assert u.port == 80
        assert u.scheme == "http"

    def test_schemehost_noport80(self):
        """Test port added with no port and http scheme in URL."""
        u = UrlParser("http://host")
        assert u.hostname == "host"
        assert u.port == 80
        assert u.scheme == "http"
