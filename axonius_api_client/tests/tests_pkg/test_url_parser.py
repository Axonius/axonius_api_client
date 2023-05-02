# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.http."""

import pytest

from axonius_api_client.projects.url_parser import UrlParser


class TestUrlParser:
    """Test UrlParser."""

    def test_scheme_host_port_443(self):
        """Test a proper URL gets parsed the same."""
        parser = UrlParser("https://host:443/blah")
        assert parser.hostname == "host"
        assert parser.port == 443
        assert parser.scheme == "https"
        assert parser.parsed.path == "/blah"
        assert parser.url_full == "https://host:443/blah"
        assert parser.url == "https://host:443"

    def test_str_repr(self):
        """Test str/repr has URL path."""
        parser = UrlParser("https://host:443/blah")
        assert parser.parsed.path in str(parser)
        assert parser.parsed.path in repr(parser)

    def test_scheme_host_no_port_443(self):
        """Test port gets added for https scheme."""
        parser = UrlParser("https://host")
        assert parser.hostname == "host"
        assert parser.port == 443
        assert parser.scheme == "https"

    def test_just_host(self):
        """Test schema added for just host."""
        parser = UrlParser("host")
        assert parser.hostname == "host"
        assert parser.port == 443
        assert parser.scheme == "https"

    def test_just_host_port(self):
        """Test schema added for just host and port."""
        parser = UrlParser("host:443")
        assert parser.hostname == "host"
        assert parser.port == 443
        assert parser.scheme == "https"

    def test_host_no_scheme_port(self):
        """Test exc when no port or scheme in URL."""
        exc = ValueError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            UrlParser("host", default_scheme="")

    def test_unknown_scheme_host_no_port(self):
        """Test exc when no port and non http/https scheme."""
        exc = ValueError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            UrlParser("httpx://host")

    def test_hostport443_with_slash(self):
        """Test scheme added with port 443 and no scheme in URL."""
        parser = UrlParser("host:443/")
        assert parser.hostname == "host"
        assert parser.port == 443
        assert parser.scheme == "https"

    def test_hostport443_no_scheme(self):
        """Test scheme added with port 443 and no scheme in URL."""
        parser = UrlParser("host:443", default_scheme="")
        assert parser.hostname == "host"
        assert parser.port == 443
        assert parser.scheme == "https"

    def test_hostport80_no_scheme(self):
        """Test scheme added with port 80 and no scheme in URL."""
        parser = UrlParser("host:80", default_scheme="")
        assert parser.hostname == "host"
        assert parser.port == 80
        assert parser.scheme == "http"

    def test_scheme_host_no_port80(self):
        """Test port added with no port and http scheme in URL."""
        # noinspection HttpUrlsUsage
        parser = UrlParser("http://host")
        assert parser.hostname == "host"
        assert parser.port == 80
        assert parser.scheme == "http"
