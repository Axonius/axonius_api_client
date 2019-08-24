# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

import axonius_api_client as axonapi


class TestUrlParser(object):
    """Test axonapi.UrlParser."""

    def test_schemehostport443(self):
        """Test a proper URL gets parsed the same."""
        u = axonapi.UrlParser("https://host:443/blah")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"
        assert u.parsed.path == "/blah"
        assert u.url_full == "https://host:443/blah"
        assert u.url == "https://host:443"

    def test_str_repr(self):
        """Test str/repr has URL path."""
        u = axonapi.UrlParser("https://host:443/blah")
        assert u.parsed.path in format(u)
        assert u.parsed.path in repr(u)

    def test_schemehost_noport443(self):
        """Test port gets added for https scheme."""
        u = axonapi.UrlParser("https://host")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_host_noschemeport(self):
        """Test exc when no port or scheme in URL."""
        exc = axonapi.HttpError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            axonapi.UrlParser("host", default_scheme="")

    def test_unknownschemehost_noport(self):
        """Test exc when no port and non http/https scheme."""
        exc = axonapi.HttpError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            axonapi.UrlParser("httpx://host")

    def test_hostport443_withslash(self):
        """Test scheme added with port 443 and no scheme in URL."""
        u = axonapi.UrlParser("host:443/")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_hostport443_noscheme(self):
        """Test scheme added with port 443 and no scheme in URL."""
        u = axonapi.UrlParser("host:443", default_scheme="")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_hostport80_noscheme(self):
        """Test scheme added with port 80 and no scheme in URL."""
        u = axonapi.UrlParser("host:80", default_scheme="")
        assert u.hostname == "host"
        assert u.port == 80
        assert u.scheme == "http"

    def test_schemehost_noport80(self):
        """Test port added with no port and http scheme in URL."""
        u = axonapi.UrlParser("http://host")
        assert u.hostname == "host"
        assert u.port == 80
        assert u.scheme == "http"
